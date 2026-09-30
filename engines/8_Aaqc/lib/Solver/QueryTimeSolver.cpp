//===-- QueryTimeSolver.cpp -----------------------------------------------===//

#include "klee/Solver.h"
#include "klee/SolverImpl.h"
#include "klee/SolverCmdLine.h"
#include "klee/OptionCategories.h"
#include "klee/Statistics.h"
#include "klee/Internal/Support/ErrorHandling.h"
#include "klee/Internal/System/Time.h"

#include "llvm/Support/CommandLine.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

#include <memory>
#include <string>

using namespace klee;

namespace {

llvm::cl::opt<std::string> SolverTimeLog(
    "solver-time-log",
    llvm::cl::desc("Log elapsed time of every query reaching the core solver "
                   "to the given CSV file"),
    llvm::cl::init(""), 
    llvm::cl::cat(klee::SolvingCat));

class QueryTimeSolver : public SolverImpl {
private:
  Solver *solver;
  std::unique_ptr<llvm::raw_fd_ostream> os;
  uint64_t queryID;

  static uint64_t instructions() {
    Statistic *s = theStatisticManager->getStatisticByName("Instructions");
    return s ? s->getValue() : 0;
  }

  void record(const char *kind, uint64_t id, uint64_t instr,
              const time::Span &elapsed, bool success) {
    *os << id << "," << kind << "," << instr << ","
        << (success ? "OK" : "FAIL") << "," << elapsed.toMicroseconds() << "\n";
    os->flush();
  }

public:
  QueryTimeSolver(Solver *_solver, const std::string &path)
      : solver(_solver), queryID(0) {
    std::error_code ec;
    os = std::unique_ptr<llvm::raw_fd_ostream>(
        new llvm::raw_fd_ostream(path.c_str(), ec, llvm::sys::fs::F_Text));
    if (ec)
      klee_error("Write to %s failed: %s", path.c_str(), ec.message().c_str());
    *os << "query_id,kind,instructions,status,elapsed_us\n";
    os->flush();
  }

  ~QueryTimeSolver() { delete solver; }

  bool computeTruth(const Query &query, bool &isValid) {
    uint64_t id = queryID++, instr = instructions();
    time::Point start = time::getWallTime();
    bool success = solver->impl->computeTruth(query, isValid);
    record("Truth", id, instr, time::getWallTime() - start, success);
    return success;
  }

  bool computeValue(const Query &query, ref<Expr> &result) {
    uint64_t id = queryID++, instr = instructions();
    time::Point start = time::getWallTime();
    bool success = solver->impl->computeValue(query, result);
    record("Value", id, instr, time::getWallTime() - start, success);
    return success;
  }

  bool computeInitialValues(const Query &query,
                            const std::vector<const Array *> &objects,
                            std::vector<std::vector<unsigned char> > &values,
                            bool &hasSolution) {
    uint64_t id = queryID++, instr = instructions();
    time::Point start = time::getWallTime();
    bool success = solver->impl->computeInitialValues(query, objects, values,
                                                      hasSolution);
    record("InitialValues", id, instr, time::getWallTime() - start, success);
    return success;
  }

  SolverRunStatus getOperationStatusCode() {
    return solver->impl->getOperationStatusCode();
  }

  char *getConstraintLog(const Query &query) {
    return solver->impl->getConstraintLog(query);
  }

  void setCoreSolverTimeout(time::Span timeout) {
    solver->impl->setCoreSolverTimeout(timeout);
  }
};

} // namespace

namespace klee {

Solver *createQueryTimeSolver(Solver *s) {
  if (SolverTimeLog.empty())
    return s;
  klee_message("Logging core-solver query times to %s",
               SolverTimeLog.c_str());
  return new Solver(new QueryTimeSolver(s, SolverTimeLog));
}

} // namespace klee