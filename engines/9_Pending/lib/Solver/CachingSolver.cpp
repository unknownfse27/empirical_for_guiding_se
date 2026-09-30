//===-- CachingSolver.cpp - Caching expression solver ---------------------===//
//
//                     The KLEE Symbolic Virtual Machine
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//


#include "klee/Solver/Solver.h"

#include "klee/Expr/Constraints.h"
#include "klee/Expr/Expr.h"
#include "klee/Solver/IncompleteSolver.h"
#include "klee/Solver/SolverImpl.h"
#include "klee/Solver/SolverStats.h"

#include <ciso646>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <string>

#ifdef _LIBCPP_VERSION
#include <unordered_map>
#define unordered_map std::unordered_map
#else
#include <tr1/unordered_map>
#define unordered_map std::tr1::unordered_map
#endif

using namespace klee;

class CachingSolver : public SolverImpl {
private:
  ref<Expr> canonicalizeQuery(ref<Expr> originalQuery,
                              bool &negationUsed);

  void cacheInsert(const Query& query,
                   IncompleteSolver::PartialValidity result);

  bool cacheLookup(const Query& query,
                   IncompleteSolver::PartialValidity &result);
  
  struct CacheEntry {
    CacheEntry(const ConstraintManager &c, ref<Expr> q)
      : constraints(c), query(q) {}

    CacheEntry(const CacheEntry &ce)
      : constraints(ce.constraints), query(ce.query) {}
    
    ConstraintManager constraints;
    ref<Expr> query;

    bool operator==(const CacheEntry &b) const {
      return constraints==b.constraints && *query.get()==*b.query.get();
    }
  };

  struct CacheEntryHash {
    unsigned operator()(const CacheEntry &ce) const {
      unsigned result = ce.query->hash();

      for (auto const &constraint : ce.constraints) {
        result ^= constraint->hash();
      }

      return result;
    }
  };

  typedef unordered_map<CacheEntry, 
                        IncompleteSolver::PartialValidity, 
                        CacheEntryHash> cache_map;
  
  Solver *solver;
  cache_map cache;

  // [NEW] per-run cache hit summary
  uint64_t runTotalQueries = 0;
  uint64_t runHitQueries   = 0;

  static inline std::string joinPath(const std::string& base,
                                     const char* name) {
    if (base.empty()) return std::string(name);
    if (base[base.size()-1] == '/') return base + name;
    return base + "/" + name;
  }

  static inline void ensureDirBestEffort(const std::string& dir) {
    if (dir.empty()) return;
    // Avoid filesystem dependency; best-effort mkdir -p
    // If dir contains quotes, skip to avoid shell issues.
    if (dir.find('"') != std::string::npos) return;
    std::string cmd = "mkdir -p \"" + dir + "\"";
    (void)std::system(cmd.c_str());
  }

public:
  CachingSolver(Solver *s) : solver(s) {}
  ~CachingSolver() {
    // [NEW] Always append per-run hit summary to cache_result.log
    const char* outDirEnv = std::getenv("KLEE_OUTPUT_DIR");
    std::string outDir =
        (outDirEnv && *outDirEnv) ? std::string(outDirEnv)
                                  : std::string("klee-last");
    ensureDirBestEffort(outDir);

    const std::string logPath = joinPath(outDir, "cache_result.log");
    std::ofstream sf(logPath.c_str(), std::ios::out | std::ios::app);
    if (sf.good()) {
      using namespace std::chrono;
      const uint64_t epoch_ms =
        (uint64_t)duration_cast<milliseconds>(
          system_clock::now().time_since_epoch()).count();

      double hitRate = 0.0;
      if (runTotalQueries)
        hitRate = (double)runHitQueries / (double)runTotalQueries;

      // format: epoch_ms total hit hitRate
      sf << epoch_ms << ' '
         << runTotalQueries << ' '
         << runHitQueries << ' '
         << hitRate
         << '\n';
      sf.flush();
    }

    cache.clear();
    delete solver;
  }

  bool computeValidity(const Query&, Solver::Validity &result);
  bool computeTruth(const Query&, bool &isValid);
  bool computeValue(const Query& query, ref<Expr> &result) {
    ++stats::queryCacheMisses;
    return solver->impl->computeValue(query, result);
  }
  bool computeInitialValues(const Query& query,
                            const std::vector<const Array*> &objects,
                            std::vector< std::vector<unsigned char> > &values,
                            bool &hasSolution) {
    ++stats::queryCacheMisses;
    return solver->impl->computeInitialValues(query, objects, values, 
                                              hasSolution);
  }
  SolverRunStatus getOperationStatusCode();
  char *getConstraintLog(const Query&);
  void setCoreSolverTimeout(time::Span timeout);
};

/** @returns the canonical version of the given query.  The reference
    negationUsed is set to true if the original query was negated in
    the canonicalization process. */
ref<Expr> CachingSolver::canonicalizeQuery(ref<Expr> originalQuery,
                                           bool &negationUsed) {
  ref<Expr> negatedQuery = Expr::createIsZero(originalQuery);

  // select the "smaller" query to the be canonical representation
  if (originalQuery.compare(negatedQuery) < 0) {
    negationUsed = false;
    return originalQuery;
  } else {
    negationUsed = true;
    return negatedQuery;
  }
}

/** @returns true on a cache hit, false of a cache miss.  Reference
    value result only valid on a cache hit. */
bool CachingSolver::cacheLookup(const Query& query,
                                IncompleteSolver::PartialValidity &result) {
  bool negationUsed;
  ref<Expr> canonicalQuery = canonicalizeQuery(query.expr, negationUsed);

  ++runTotalQueries;

  CacheEntry ce(query.constraints, canonicalQuery);
  cache_map::iterator it = cache.find(ce);
  
  if (it != cache.end()) {
    ++runHitQueries;
    result = (negationUsed ?
              IncompleteSolver::negatePartialValidity(it->second) :
              it->second);
    return true;
  }
  
  return false;
}

/// Inserts the given query, result pair into the cache.
void CachingSolver::cacheInsert(const Query& query,
                                IncompleteSolver::PartialValidity result) {
  bool negationUsed;
  ref<Expr> canonicalQuery = canonicalizeQuery(query.expr, negationUsed);

  CacheEntry ce(query.constraints, canonicalQuery);
  IncompleteSolver::PartialValidity cachedResult = 
    (negationUsed ? IncompleteSolver::negatePartialValidity(result) : result);
  
  cache.insert(std::make_pair(ce, cachedResult));
}

bool CachingSolver::computeValidity(const Query& query,
                                    Solver::Validity &result) {
  IncompleteSolver::PartialValidity cachedResult;
  bool tmp, cacheHit = cacheLookup(query, cachedResult);
  
  if (cacheHit) {
    switch(cachedResult) {
    case IncompleteSolver::MustBeTrue:   
      result = Solver::True;
      ++stats::queryCacheHits;
      return true;
    case IncompleteSolver::MustBeFalse:  
      result = Solver::False;
      ++stats::queryCacheHits;
      return true;
    case IncompleteSolver::TrueOrFalse:  
      result = Solver::Unknown;
      ++stats::queryCacheHits;
      return true;
    case IncompleteSolver::MayBeTrue: {
      ++stats::queryCacheMisses;
      if (!solver->impl->computeTruth(query, tmp))
        return false;
      if (tmp) {
        cacheInsert(query, IncompleteSolver::MustBeTrue);
        result = Solver::True;
        return true;
      } else {
        cacheInsert(query, IncompleteSolver::TrueOrFalse);
        result = Solver::Unknown;
        return true;
      }
    }
    case IncompleteSolver::MayBeFalse: {
      ++stats::queryCacheMisses;
      if (!solver->impl->computeTruth(query.negateExpr(), tmp))
        return false;
      if (tmp) {
        cacheInsert(query, IncompleteSolver::MustBeFalse);
        result = Solver::False;
        return true;
      } else {
        cacheInsert(query, IncompleteSolver::TrueOrFalse);
        result = Solver::Unknown;
        return true;
      }
    }
    default: assert(0 && "unreachable");
    }
  }

  ++stats::queryCacheMisses;
  
  if (!solver->impl->computeValidity(query, result))
    return false;

  switch (result) {
  case Solver::True: 
    cachedResult = IncompleteSolver::MustBeTrue; break;
  case Solver::False: 
    cachedResult = IncompleteSolver::MustBeFalse; break;
  default: 
    cachedResult = IncompleteSolver::TrueOrFalse; break;
  }
  
  cacheInsert(query, cachedResult);
  return true;
}

bool CachingSolver::computeTruth(const Query& query,
                                 bool &isValid) {
  IncompleteSolver::PartialValidity cachedResult;
  bool cacheHit = cacheLookup(query, cachedResult);

  // a cached result of MayBeTrue forces us to check whether
  // a False assignment exists.
  if (cacheHit && cachedResult != IncompleteSolver::MayBeTrue) {
    ++stats::queryCacheHits;
    isValid = (cachedResult == IncompleteSolver::MustBeTrue);
    return true;
  }

  ++stats::queryCacheMisses;
  
  // cache miss: query solver
  if (!solver->impl->computeTruth(query, isValid))
    return false;

  if (isValid) {
    cachedResult = IncompleteSolver::MustBeTrue;
  } else if (cacheHit) {
    // We know a true assignment exists, and query isn't valid, so
    // must be TrueOrFalse.
    assert(cachedResult == IncompleteSolver::MayBeTrue);
    cachedResult = IncompleteSolver::TrueOrFalse;
  } else {
    cachedResult = IncompleteSolver::MayBeFalse;
  }
  
  cacheInsert(query, cachedResult);
  return true;
}

SolverImpl::SolverRunStatus CachingSolver::getOperationStatusCode() {
  return solver->impl->getOperationStatusCode();
}

char *CachingSolver::getConstraintLog(const Query& query) {
  return solver->impl->getConstraintLog(query);
}

void CachingSolver::setCoreSolverTimeout(time::Span timeout) {
  solver->impl->setCoreSolverTimeout(timeout);
}

///

Solver *klee::createCachingSolver(Solver *_solver) {
  return new Solver(new CachingSolver(_solver));
}
