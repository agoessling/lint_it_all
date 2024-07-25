py_binary(
    name = "init_repo",
    srcs = ["init_repo.py"],
    data = ["//:init_files"],
    args = [
        "--init_files $(rlocationpaths //:init_files)",
        "--this $(rlocationpath :init_repo.py)",
    ],
    visibility = ["//visibility:public"],
    deps = ["@bazel_tools//tools/python/runfiles"],
)
