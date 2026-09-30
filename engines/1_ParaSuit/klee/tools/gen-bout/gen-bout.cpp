//===-- gen-bout.cpp --------------------------------------------*- C++ -*-===//
//
//                     The KLEE Symbolic Virtual Machine
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#include "klee/Internal/ADT/KTest.h"

#if defined(__FreeBSD__) || defined(__minix)
#define stat64 stat
#endif


#define MAX 200
/* KLEE names symbolic files 'A' + k in klee_init_fds(), so 26 is the ceiling. */
#define MAX_SYM_FILES 26

static void push_obj(KTest *b, const char *name, unsigned total_bytes,
                     unsigned char *bytes) {
  assert(b->numObjects < MAX);
  KTestObject *o = &b->objects[b->numObjects++];

  o->name = strdup(name);
  o->numBytes = total_bytes;
  o->bytes = (unsigned char *)malloc(o->numBytes);

  memcpy(o->bytes, bytes, total_bytes);
}

static void push_range(KTest *b, const char *name, unsigned value) {
  assert(b->numObjects < MAX);
  KTestObject *o = &b->objects[b->numObjects++];

  o->name = strdup(name);
  o->numBytes = 4;
  o->bytes = (unsigned char *)malloc(o->numBytes);

  *(unsigned *)o->bytes = value;
}

void print_usage_and_exit(char *program_name) {
  fprintf(stderr,
    "%s: Tool for generating a ktest file from concrete input, e.g., for using a concrete crashing input as a ktest seed.\n"
    "Usage: %s <arguments>\n"
    "       <arguments> are the command-line arguments of the program, with the following treated as special:\n"
    "       --bout-file <filename>      - Specifying the output file name for the ktest file (default: file.bout).\n"
    "       --sym-stdin <filename>      - Specifying a file that is the content of stdin (only once).\n"
    "       --sym-stdout <filename>     - Specifying a file that is the content of stdout (only once).\n"
    "       --sym-file <filename>       - Specifying a file that is the content of a symbolic file provided to\n"
    "                                     the program. May be repeated up to %d times; the k-th occurrence maps\n"
    "                                     to KLEE's symbolic file 'A' + k (A, B, C, ...).\n"
    "                                     NOTE: KLEE's -sym-files N L gives every file the SAME length, so all\n"
    "                                     contents are zero-padded to the size of the largest one.\n"
    "   Ex: %s -o -p -q file1 --sym-stdin file2 --sym-file f_A --sym-file f_B --sym-stdout file4\n",
    program_name, program_name, MAX_SYM_FILES, program_name);
  exit(1);
}

/* Read a whole file into a freshly malloc'd buffer; returns NULL on failure. */
static unsigned char *read_whole_file(const char *filename,
                                      struct stat64 *file_stat) {
  FILE *fp = fopen(filename, "rb");
  if (fp == NULL)
    return NULL;

  if (stat64(filename, file_stat) < 0) {
    fclose(fp);
    return NULL;
  }

  long nbytes = (long)file_stat->st_size;
  /* malloc(0) is allowed to return NULL, so always ask for at least 1 byte. */
  unsigned char *content = (unsigned char *)malloc(nbytes > 0 ? nbytes : 1);
  if (content == NULL) {
    fclose(fp);
    fputs("Memory allocation failure\n", stderr);
    exit(1);
  }

  if (nbytes > 0 && fread(content, 1, nbytes, fp) != (size_t)nbytes) {
    free(content);
    fclose(fp);
    return NULL;
  }

  fclose(fp);
  return content;
}

int main(int argc, char *argv[]) {
  unsigned i, argv_copy_idx;
  unsigned file_counter = 0;
  char *stdout_content_filename = NULL;
  char *stdin_content_filename = NULL;
  char *content_filenames_list[MAX_SYM_FILES];
  char **argv_copy;
  char *bout_file = NULL;

  if (argc < 2)
    print_usage_and_exit(argv[0]);

  KTest b;
  b.symArgvs = 0;
  b.symArgvLen = 0;

  b.numObjects = 0;
  b.objects = (KTestObject *)malloc(MAX * sizeof *b.objects);

  if ((argv_copy = (char **)malloc(sizeof(char *) * (argc * 2 + 8))) == NULL) {
    fprintf(stderr, "Could not allocate more memory\n");
    return 1;
  }

  argv_copy[0] = (char *)malloc(strlen(argv[0]) + 1);
  strcpy(argv_copy[0], argv[0]);
  argv_copy_idx = 1;

  for (i = 1; i < (unsigned)argc; i++) {
    if (strcmp(argv[i], "--sym-stdout") == 0 ||
        strcmp(argv[i], "-sym-stdout") == 0) {
      if (++i == (unsigned)argc || argv[i][0] == '-')
        print_usage_and_exit(argv[0]);

      if (stdout_content_filename)
        print_usage_and_exit(argv[0]);

      stdout_content_filename = argv[i];

    } else if (strcmp(argv[i], "--sym-stdin") == 0 ||
               strcmp(argv[i], "-sym-stdin") == 0) {
      if (++i == (unsigned)argc || argv[i][0] == '-')
        print_usage_and_exit(argv[0]);

      if (stdin_content_filename)
        print_usage_and_exit(argv[0]);

      stdin_content_filename = argv[i];
    } else if (strcmp(argv[i], "--sym-file") == 0 ||
               strcmp(argv[i], "-sym-file") == 0) {
      if (++i == (unsigned)argc || argv[i][0] == '-')
        print_usage_and_exit(argv[0]);

      if (file_counter >= MAX_SYM_FILES) {
        fprintf(stderr, "At most %d --sym-file arguments are supported\n",
                MAX_SYM_FILES);
        exit(1);
      }

      content_filenames_list[file_counter++] = argv[i];
    } else if (strcmp(argv[i], "--bout-file") == 0 ||
               strcmp(argv[i], "-bout-file") == 0) {
      if (++i == (unsigned)argc)
        print_usage_and_exit(argv[0]);

      bout_file = argv[i];
    } else {
      long nbytes = strlen(argv[i]) + 1;
      static int total_args = 0;

      char arg[1024];
      snprintf(arg, sizeof(arg), "arg%02d", total_args++);
      push_obj(&b, (const char *)arg, nbytes, (unsigned char *)argv[i]);

      char *buf1 = (char *)malloc(1024);
      char *buf2 = (char *)malloc(1024);
      strcpy(buf1, "-sym-arg");
      snprintf(buf2, 1024, "%ld", nbytes - 1);
      argv_copy[argv_copy_idx++] = buf1;
      argv_copy[argv_copy_idx++] = buf2;
    }
  }

  if (file_counter > 0) {
    unsigned char *contents[MAX_SYM_FILES];
    struct stat64 stats[MAX_SYM_FILES];
    long sizes[MAX_SYM_FILES];
    long max_size = 0;

    /* Pass 1: slurp every file and find the largest size. */
    for (i = 0; i < file_counter; ++i) {
      const char *fn = content_filenames_list[i];

      contents[i] = read_whole_file(fn, &stats[i]);
      if (contents[i] == NULL) {
        fprintf(stderr, "Failure opening/reading %s\n", fn);
        print_usage_and_exit(argv[0]);
      }

      sizes[i] = (long)stats[i].st_size;
      if (sizes[i] > max_size)
        max_size = sizes[i];
    }

    if (max_size == 0) {
      fputs("All --sym-file inputs are empty; KLEE requires a non-zero "
            "file length\n", stderr);
      exit(1);
    }

    /* Pass 2: zero-pad each file to max_size and push it as A-data, B-data, ...
       KLEE's -sym-files N L allocates N files of L bytes each, and the seeding
       code matches objects positionally, so both the order and the sizes have
       to line up exactly. */
    for (i = 0; i < file_counter; ++i) {
      char filename[8];
      char statname[16];

      snprintf(filename, sizeof(filename), "%c-data", (char)('A' + i));
      snprintf(statname, sizeof(statname), "%s-stat", filename);

      unsigned char *padded = (unsigned char *)calloc(max_size, 1);
      if (padded == NULL) {
        fputs("Memory allocation failure\n", stderr);
        exit(1);
      }
      memcpy(padded, contents[i], sizes[i]);

      /* Keep the stat consistent with the padded content. */
      stats[i].st_size = max_size;

      push_obj(&b, filename, max_size, padded);
      push_obj(&b, statname, sizeof(struct stat64), (unsigned char *)&stats[i]);

      free(padded);
      free(contents[i]);
    }

    char *buf1 = (char *)malloc(1024);
    char *buf2 = (char *)malloc(1024);
    char *buf3 = (char *)malloc(1024);
    snprintf(buf1, 1024, "-sym-files");
    snprintf(buf2, 1024, "%u", file_counter);
    snprintf(buf3, 1024, "%ld", max_size);
    argv_copy[argv_copy_idx++] = buf1;
    argv_copy[argv_copy_idx++] = buf2;
    argv_copy[argv_copy_idx++] = buf3;
  }

  if (stdin_content_filename) {
    struct stat64 file_stat;
    char filename[6] = "stdin";
    char statname[11] = "stdin-stat";

    unsigned char *file_content =
        read_whole_file(stdin_content_filename, &file_stat);
    if (file_content == NULL) {
      fprintf(stderr, "Failure opening %s\n", stdin_content_filename);
      print_usage_and_exit(argv[0]);
    }

    push_obj(&b, filename, file_stat.st_size, file_content);
    push_obj(&b, statname, sizeof(struct stat64), (unsigned char *)&file_stat);

    free(file_content);

    char *buf1 = (char *)malloc(1024);
    char *buf2 = (char *)malloc(1024);
    snprintf(buf1, 1024, "-sym-stdin");
    snprintf(buf2, 1024, "%ld", (long)file_stat.st_size);
    argv_copy[argv_copy_idx++] = buf1;
    argv_copy[argv_copy_idx++] = buf2;
  }

  if (stdout_content_filename) {
    struct stat64 file_stat;
    unsigned char file_content[1024];
    char filename[7] = "stdout";
    char statname[12] = "stdout-stat";

    unsigned char *raw = read_whole_file(stdout_content_filename, &file_stat);
    if (raw == NULL) {
      fprintf(stderr, "Failure opening %s\n", stdout_content_filename);
      print_usage_and_exit(argv[0]);
    }

    long copy = (long)file_stat.st_size < 1024 ? (long)file_stat.st_size : 1024;
    memset(file_content, 0, sizeof(file_content));
    memcpy(file_content, raw, copy);
    free(raw);

    /* KLEE always models stdout as a 1024-byte file. */
    file_stat.st_size = 1024;

    push_obj(&b, filename, 1024, file_content);
    push_obj(&b, statname, sizeof(struct stat64), (unsigned char *)&file_stat);

    char *buf = (char *)malloc(1024);
    snprintf(buf, 1024, "-sym-stdout");
    argv_copy[argv_copy_idx++] = buf;
  }

  argv_copy[argv_copy_idx] = 0;

  b.numArgs = argv_copy_idx;
  b.args = argv_copy;

  push_range(&b, "model_version", 1);

  if (!kTest_toFile(&b, bout_file ? bout_file : "file.bout"))
    assert(0);

  for (int i = 0; i < (int)b.numObjects; ++i) {
    free(b.objects[i].name);
    free(b.objects[i].bytes);
  }
  free(b.objects);

  for (int i = 0; i < (int)argv_copy_idx; ++i) {
    free(argv_copy[i]);
  }
  free(argv_copy);

  return 0;
}