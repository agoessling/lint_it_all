exports_files([".clang-tidy"])

filegroup(
    name = "init_files",
    srcs = [
        ".clang-tidy",
        ".clang-format",
        ".bazeliskrc",
    ] +
    glob([".aspect/**"]),
    visibility = ["//visibility:public"],
)

cc_binary(
    name = "hello_world",
    srcs = ["hello_world.c"],
)
