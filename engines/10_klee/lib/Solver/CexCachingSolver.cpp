//===-- CexCachingSolver.cpp ----------------------------------------------===//
//
//                     The KLEE Symbolic Virtual Machine
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#include "klee/Solver/Solver.h"

#include "klee/Expr/Assignment.h"
#include "klee/Expr/Constraints.h"
#include "klee/Expr/Expr.h"
#include "klee/Expr/ExprUtil.h"
#include "klee/Expr/ExprVisitor.h"
#include "klee/Internal/ADT/MapOfSets.h"
#include "klee/Internal/Support/ErrorHandling.h"
#include "klee/OptionCategories.h"
#include "klee/Solver/SolverImpl.h"
#include "klee/Solver/SolverStats.h"
#include "klee/TimerStatIncrementer.h"

#include "llvm/Support/CommandLine.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace klee;
using namespace llvm;

namespace {
cl::opt<bool> DebugCexCacheCheckBinding(
    "debug-cex-cache-check-binding", cl::init(false),
    cl::desc("Debug the correctness of the counterexample "
             "cache assignments (default=false)"),
    cl::cat(SolvingCat));

cl::opt<bool>
    CexCacheTryAll("cex-cache-try-all", cl::init(false),
                   cl::desc("Try substituting all counterexamples before "
                            "asking the SMT solver (default=false)"),
                   cl::cat(SolvingCat));

cl::opt<bool>
    CexCacheSuperSet("cex-cache-superset", cl::init(false),
                     cl::desc("Try substituting SAT superset counterexample "
                              "before asking the SMT solver (default=false)"),
                     cl::cat(SolvingCat));

cl::opt<bool> CexCacheExperimental(
    "cex-cache-exp", cl::init(false),
    cl::desc("Optimization for validity queries (default=false)"),
    cl::cat(SolvingCat));

cl::opt<std::string> SeedArgsFile(
    "seed-args-file",
    cl::init(""),
    cl::desc("Path to seed_args.txt"),
    cl::cat(SolvingCat));

cl::opt<std::string> SeedArgsLog(
    "seed-args-log",
    cl::init("seed_args_hit.log"),
    cl::desc("Path to seed argument hit log"),
    cl::cat(SolvingCat));

cl::opt<unsigned> SeedArgsMaxCombinations(
    "seed-args-max-combinations",
    cl::init(10000),
    cl::desc("Maximum seed argument combinations checked per query"),
    cl::cat(SolvingCat));

} // namespace

///

typedef std::set< ref<Expr> > KeyType;

struct AssignmentLessThan {
  bool operator()(const Assignment *a, const Assignment *b) const {
    return a->bindings < b->bindings;
  }
};


class CexCachingSolver : public SolverImpl {
  typedef std::set<Assignment*, AssignmentLessThan> assignmentsTable_ty;

  Solver *solver;
  
  MapOfSets<ref<Expr>, Assignment*> cache;
  // memo table
  assignmentsTable_ty assignmentsTable;

  typedef std::map<std::string, std::vector<std::vector<unsigned char>>> seed_args_ty;

  seed_args_ty seedArgs;

  unsigned long seedQueryAttempts;
  unsigned long seedQueryEligible;
  unsigned long seedQueryHits;
  unsigned long seedSolverSkips;

  bool loadSeedArgs(const std::string &path);

  bool trySeedAssignment(KeyType &key,
                         const std::vector<const Array*> &objects,
                         Assignment *&result);

  bool trySeedAssignmentRecursive(
      KeyType &key,
      const std::vector<const Array*> &objects,
      unsigned index,
      std::vector<std::vector<unsigned char> > &values,
      unsigned &numTried,
      Assignment *&result);

  void logSeedHit(const std::vector<const Array*> &objects,
                  unsigned numTried);

  void logSeedSummary();

  bool searchForAssignment(KeyType &key, 
                           Assignment *&result);
  
  bool lookupAssignment(const Query& query, KeyType &key, Assignment *&result);

  bool lookupAssignment(const Query& query, Assignment *&result) {
    KeyType key;
    return lookupAssignment(query, key, result);
  }

  bool getAssignment(const Query& query, Assignment *&result);
  
public:
  CexCachingSolver(Solver *_solver): 
        solver(_solver),
        seedQueryAttempts(0),
        seedQueryEligible(0),
        seedQueryHits(0),
        seedSolverSkips(0) {

    if (!SeedArgsFile.empty())
      loadSeedArgs(SeedArgsFile);
  }
  ~CexCachingSolver();
  
  bool computeTruth(const Query&, bool &isValid);
  bool computeValidity(const Query&, Solver::Validity &result);
  bool computeValue(const Query&, ref<Expr> &result);
  bool computeInitialValues(const Query&,
                            const std::vector<const Array*> &objects,
                            std::vector< std::vector<unsigned char> > &values,
                            bool &hasSolution);
  SolverRunStatus getOperationStatusCode();
  char *getConstraintLog(const Query& query);
  void setCoreSolverTimeout(time::Span timeout);
};

///

bool CexCachingSolver::loadSeedArgs(
    const std::string &path) {

  std::ifstream input(path.c_str());

  if (!input.is_open()) {
    llvm::errs()
        << "[SeedArgs] Failed to open: "
        << path << "\n";
    return false;
  }

  std::string argName;
  std::string hexValue;

  unsigned totalValues = 0;

  while (input >> argName >> hexValue) {

    // arg00, arg01, ...
    if (argName.size() < 4 ||
        argName.substr(0, 3) != "arg") {
      continue;
    }

    bool validName = true;

    for (size_t i = 3; i < argName.size(); ++i) {
      if (!std::isdigit(
              static_cast<unsigned char>(argName[i]))) {
        validName = false;
        break;
      }
    }

    if (!validName)
      continue;

    if (hexValue.size() % 2 != 0) {
      llvm::errs()
          << "[SeedArgs] Invalid hex length: "
          << argName << " "
          << hexValue << "\n";
      continue;
    }

    std::vector<unsigned char> value;

    bool validHex = true;

    for (size_t i = 0; i < hexValue.size(); i += 2) {
      char h1 = hexValue[i];
      char h2 = hexValue[i + 1];

      unsigned v1;
      unsigned v2;

      if (h1 >= '0' && h1 <= '9')
        v1 = h1 - '0';
      else if (h1 >= 'a' && h1 <= 'f')
        v1 = h1 - 'a' + 10;
      else if (h1 >= 'A' && h1 <= 'F')
        v1 = h1 - 'A' + 10;
      else {
        validHex = false;
        break;
      }

      if (h2 >= '0' && h2 <= '9')
        v2 = h2 - '0';
      else if (h2 >= 'a' && h2 <= 'f')
        v2 = h2 - 'a' + 10;
      else if (h2 >= 'A' && h2 <= 'F')
        v2 = h2 - 'A' + 10;
      else {
        validHex = false;
        break;
      }

      value.push_back(
          static_cast<unsigned char>(
              (v1 << 4) | v2));
    }

    if (!validHex) {
      llvm::errs()
          << "[SeedArgs] Invalid hex value: "
          << argName << " "
          << hexValue << "\n";
      continue;
    }

    seedArgs[argName].push_back(value);
    ++totalValues;
  }

  llvm::errs()
      << "[SeedArgs] Loaded "
      << totalValues
      << " values for "
      << seedArgs.size()
      << " arguments from "
      << path << "\n";

  return true;
}

bool CexCachingSolver::trySeedAssignmentRecursive(
    KeyType &key,
    const std::vector<const Array*> &objects,
    unsigned index,
    std::vector<std::vector<unsigned char> > &values,
    unsigned &numTried,
    Assignment *&result) {

  if (index == objects.size()) {
    if (numTried >= SeedArgsMaxCombinations)
      return false;

    ++numTried;

    Assignment *candidate =
        new Assignment(objects, values);

    /*
     * key is the exact CEX-cache query:
     *
     *   query.constraints AND !query.expr
     *
     * Only skip the SMT solver if the seed-generated
     * assignment actually satisfies the entire key.
     */
    if (candidate->satisfies(
            key.begin(), key.end())) {
      result = candidate;
      return true;
    }

    delete candidate;
    return false;
  }

  const Array *object = objects[index];

  seed_args_ty::const_iterator seedIt =
      seedArgs.find(object->name);

  /*
   * The query contains a symbolic object for which no seed
   * values are available. We cannot safely decide this query
   * using the seed dictionary alone.
   */
  if (seedIt == seedArgs.end())
    return false;

  const std::vector<std::vector<unsigned char> >
      &candidates = seedIt->second;

  for (std::vector<std::vector<unsigned char> >::const_iterator
           it = candidates.begin(),
           ie = candidates.end();
       it != ie; ++it) {

    if (numTried >= SeedArgsMaxCombinations)
      return false;

    const std::vector<unsigned char> &candidate = *it;

    /*
     * A value longer than the KLEE symbolic Array
     * cannot be used for this object.
     */
    if (candidate.size() > object->size)
      continue;

    /*
     * Assignment expects object->size bytes.
     * Shorter seed arguments are padded with zero.
     */
    std::vector<unsigned char> normalized(
        object->size, 0);

    std::copy(candidate.begin(),
              candidate.end(),
              normalized.begin());

    values.push_back(normalized);

    if (trySeedAssignmentRecursive(
            key,
            objects,
            index + 1,
            values,
            numTried,
            result))
      return true;

    values.pop_back();
  }

  return false;
}

bool CexCachingSolver::trySeedAssignment(
    KeyType &key,
    const std::vector<const Array*> &objects,
    Assignment *&result) {

  if (SeedArgsFile.empty())
    return false;

  if (objects.empty())
    return false;

  ++seedQueryAttempts;

  /*
   * IMPORTANT:
   *
   * Every symbolic object used by this query must have
   * candidates in seed_args.txt.
   *
   * Otherwise an unbound object could effectively become
   * a zero-filled value during Assignment evaluation.
   */
  for (std::vector<const Array*>::const_iterator
           it = objects.begin(),
           ie = objects.end();
       it != ie; ++it) {

    if (seedArgs.find((*it)->name) ==
        seedArgs.end())
      return false;
  }

  ++seedQueryEligible;
  unsigned numTried = 0;

  std::vector<std::vector<unsigned char> >
      currentValues;

  result = 0;

  bool hit = trySeedAssignmentRecursive(key, objects, 0, currentValues, numTried, result);

  if (hit) {
    ++seedQueryHits;
    ++seedSolverSkips;

    logSeedHit(objects, numTried);
  }

  return hit;
}

void CexCachingSolver::logSeedHit(
    const std::vector<const Array*> &objects,
    unsigned numTried) {

  if (SeedArgsLog.empty())
    return;

  std::ofstream log(
      SeedArgsLog.c_str(),
      std::ios::out | std::ios::app);

  if (!log.is_open())
    return;

  log << "HIT " << seedQueryHits << " tried=" << numTried << " objects=";

  for (unsigned i = 0;
       i < objects.size();
       ++i) {

    if (i != 0)
      log << ",";

    log << objects[i]->name;
  }

  log << "\n";
}

void CexCachingSolver::logSeedSummary() {

  if (SeedArgsLog.empty())
    return;

  std::ofstream log(
      SeedArgsLog.c_str(),
      std::ios::out | std::ios::app);

  if (!log.is_open())
    return;

  log << "=== SeedArgs Summary ===\n";
  log << "seed_query_attempts="
      << seedQueryAttempts << "\n";
  log << "seed_query_eligible="
      << seedQueryEligible << "\n";
  log << "seed_query_hits="
      << seedQueryHits << "\n";
  log << "seed_solver_skips="
      << seedSolverSkips << "\n";
}

struct NullAssignment {
  bool operator()(Assignment *a) const { return !a; }
};

struct NonNullAssignment {
  bool operator()(Assignment *a) const { return a!=0; }
};

struct NullOrSatisfyingAssignment {
  KeyType &key;
  
  NullOrSatisfyingAssignment(KeyType &_key) : key(_key) {}

  bool operator()(Assignment *a) const { 
    return !a || a->satisfies(key.begin(), key.end()); 
  }
};

/// searchForAssignment - Look for a cached solution for a query.
///
/// \param key - The query to look up.
/// \param result [out] - The cached result, if the lookup is successful. This is
/// either a satisfying assignment (for a satisfiable query), or 0 (for an
/// unsatisfiable query).
/// \return - True if a cached result was found.
bool CexCachingSolver::searchForAssignment(KeyType &key, Assignment *&result) {
  Assignment * const *lookup = cache.lookup(key);
  if (lookup) {
    result = *lookup;
    return true;
  }

  if (CexCacheTryAll) {
    // Look for a satisfying assignment for a superset, which is trivially an
    // assignment for any subset.
    Assignment **lookup = 0;
    if (CexCacheSuperSet)
      lookup = cache.findSuperset(key, NonNullAssignment());

    // Otherwise, look for a subset which is unsatisfiable, see below.
    if (!lookup) 
      lookup = cache.findSubset(key, NullAssignment());

    // If either lookup succeeded, then we have a cached solution.
    if (lookup) {
      result = *lookup;
      return true;
    }

    // Otherwise, iterate through the set of current assignments to see if one
    // of them satisfies the query.
    for (assignmentsTable_ty::iterator it = assignmentsTable.begin(), 
           ie = assignmentsTable.end(); it != ie; ++it) {
      Assignment *a = *it;
      if (a->satisfies(key.begin(), key.end())) {
        result = a;
        return true;
      }
    }
  } else {
    // FIXME: Which order? one is sure to be better.

    // Look for a satisfying assignment for a superset, which is trivially an
    // assignment for any subset.
    Assignment **lookup = 0;
    if (CexCacheSuperSet)
      lookup = cache.findSuperset(key, NonNullAssignment());

    // Otherwise, look for a subset which is unsatisfiable -- if the subset is
    // unsatisfiable then no additional constraints can produce a valid
    // assignment. While searching subsets, we also explicitly the solutions for
    // satisfiable subsets to see if they solve the current query and return
    // them if so. This is cheap and frequently succeeds.
    if (!lookup) 
      lookup = cache.findSubset(key, NullOrSatisfyingAssignment(key));

    // If either lookup succeeded, then we have a cached solution.
    if (lookup) {
      result = *lookup;
      return true;
    }
  }
  
  return false;
}

/// lookupAssignment - Lookup a cached result for the given \arg query.
///
/// \param query - The query to lookup.
/// \param key [out] - On return, the key constructed for the query.
/// \param result [out] - The cached result, if the lookup is successful. This is
/// either a satisfying assignment (for a satisfiable query), or 0 (for an
/// unsatisfiable query).
/// \return True if a cached result was found.
bool CexCachingSolver::lookupAssignment(const Query &query, 
                                        KeyType &key,
                                        Assignment *&result) {
  key = KeyType(query.constraints.begin(), query.constraints.end());
  ref<Expr> neg = Expr::createIsZero(query.expr);
  if (ConstantExpr *CE = dyn_cast<ConstantExpr>(neg)) {
    if (CE->isFalse()) {
      result = (Assignment*) 0;
      ++stats::queryCexCacheHits;
      return true;
    }
  } else {
    key.insert(neg);
  }

  bool found = searchForAssignment(key, result);
  if (found)
    ++stats::queryCexCacheHits;
  else ++stats::queryCexCacheMisses;
    
  return found;
}

bool CexCachingSolver::getAssignment(const Query& query, Assignment *&result) {
  KeyType key;
  if (lookupAssignment(query, key, result))
    return true;

  std::vector<const Array*> objects;
  findSymbolicObjects(key.begin(), key.end(), objects);

  /*
   * ============================================================
   * Seed argument fast path
   * ============================================================
   */
  Assignment *seedBinding = 0;

  if (trySeedAssignment(key, objects, seedBinding)) {
    /*
     * Memoize exactly like an SMT-generated assignment.
     */
    std::pair<assignmentsTable_ty::iterator, bool>
      res = assignmentsTable.insert(seedBinding);

    if (!res.second) {
      delete seedBinding;
      seedBinding = *res.first;
    }

    result = seedBinding;
    cache.insert(key, seedBinding);

    llvm::errs()
        << "[SeedArgs] HIT - SMT solver skipped"
        << " (total hits: "
        << seedQueryHits
        << ")\n";

    return true;
  }

  /*
   * Seed candidates did not satisfy this query.
   * Fall back to KLEE's original SMT solver.
  */

  std::vector< std::vector<unsigned char> > values;
  bool hasSolution;
  if (!solver->impl->computeInitialValues(query, objects, values, 
                                          hasSolution))
    return false;
    
  Assignment *binding;
  if (hasSolution) {
    binding = new Assignment(objects, values);

    // Memoize the result.
    std::pair<assignmentsTable_ty::iterator, bool>
      res = assignmentsTable.insert(binding);
    if (!res.second) {
      delete binding;
      binding = *res.first;
    }
    
    if (DebugCexCacheCheckBinding)
      if (!binding->satisfies(key.begin(), key.end())) {
        query.dump();
        binding->dump();
        klee_error("Generated assignment doesn't match query");
      }
  } else {
    binding = (Assignment*) 0;
  }
  
  result = binding;
  cache.insert(key, binding);

  return true;
}

///

CexCachingSolver::~CexCachingSolver() {
  logSeedSummary();

  cache.clear();
  delete solver;
  for (assignmentsTable_ty::iterator it = assignmentsTable.begin(), 
         ie = assignmentsTable.end(); it != ie; ++it)
    delete *it;
}

bool CexCachingSolver::computeValidity(const Query& query,
                                       Solver::Validity &result) {
  TimerStatIncrementer t(stats::cexCacheTime);
  Assignment *a;
  if (!getAssignment(query.withFalse(), a))
    return false;
  assert(a && "computeValidity() must have assignment");
  ref<Expr> q = a->evaluate(query.expr);
  assert(isa<ConstantExpr>(q) && 
         "assignment evaluation did not result in constant");

  if (cast<ConstantExpr>(q)->isTrue()) {
    if (!getAssignment(query, a))
      return false;
    result = !a ? Solver::True : Solver::Unknown;
  } else {
    if (!getAssignment(query.negateExpr(), a))
      return false;
    result = !a ? Solver::False : Solver::Unknown;
  }
  
  return true;
}

bool CexCachingSolver::computeTruth(const Query& query,
                                    bool &isValid) {
  TimerStatIncrementer t(stats::cexCacheTime);

  // There is a small amount of redundancy here. We only need to know
  // truth and do not really need to compute an assignment. This means
  // that we could check the cache to see if we already know that
  // state ^ query has no assignment. In that case, by the validity of
  // state, we know that state ^ !query must have an assignment, and
  // so query cannot be true (valid). This does get hits, but doesn't
  // really seem to be worth the overhead.

  if (CexCacheExperimental) {
    Assignment *a;
    if (lookupAssignment(query.negateExpr(), a) && !a)
      return false;
  }

  Assignment *a;
  if (!getAssignment(query, a))
    return false;

  isValid = !a;

  return true;
}

bool CexCachingSolver::computeValue(const Query& query,
                                    ref<Expr> &result) {
  TimerStatIncrementer t(stats::cexCacheTime);

  Assignment *a;
  if (!getAssignment(query.withFalse(), a))
    return false;
  assert(a && "computeValue() must have assignment");
  result = a->evaluate(query.expr);  
  assert(isa<ConstantExpr>(result) && 
         "assignment evaluation did not result in constant");
  return true;
}

bool 
CexCachingSolver::computeInitialValues(const Query& query,
                                       const std::vector<const Array*> 
                                         &objects,
                                       std::vector< std::vector<unsigned char> >
                                         &values,
                                       bool &hasSolution) {
  TimerStatIncrementer t(stats::cexCacheTime);
  Assignment *a;
  if (!getAssignment(query, a))
    return false;
  hasSolution = !!a;
  
  if (!a)
    return true;

  // FIXME: We should use smarter assignment for result so we don't
  // need redundant copy.
  values = std::vector< std::vector<unsigned char> >(objects.size());
  for (unsigned i=0; i < objects.size(); ++i) {
    const Array *os = objects[i];
    Assignment::bindings_ty::iterator it = a->bindings.find(os);
    
    if (it == a->bindings.end()) {
      values[i] = std::vector<unsigned char>(os->size, 0);
    } else {
      values[i] = it->second;
    }
  }
  
  return true;
}

SolverImpl::SolverRunStatus CexCachingSolver::getOperationStatusCode() {
  return solver->impl->getOperationStatusCode();
}

char *CexCachingSolver::getConstraintLog(const Query& query) {
  return solver->impl->getConstraintLog(query);
}

void CexCachingSolver::setCoreSolverTimeout(time::Span timeout) {
  solver->impl->setCoreSolverTimeout(timeout);
}

///

Solver *klee::createCexCachingSolver(Solver *_solver) {
  return new Solver(new CexCachingSolver(_solver));
}
