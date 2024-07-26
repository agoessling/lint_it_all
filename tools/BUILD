py_binary(
    name = "init_repo",
    srcs = ["init_repo.py"],
    args = [
        "--this $(rlocationpath init_repo.py)",
    ],
    visibility = ["//visibility:public"],
    deps = ["@bazel_tools//tools/python/runfiles"],
)
