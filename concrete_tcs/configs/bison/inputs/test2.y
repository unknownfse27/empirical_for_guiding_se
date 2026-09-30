%define api.value.type {union { int a; double b; }} %token A B %% S: A B;
