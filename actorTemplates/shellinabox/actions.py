def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=True)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.package.install('shellinabox')
        bin_path = cuisine.bash.cmdGetPath('shellinaboxd')
        cuisine.core.dir_ensure('$BINDIR')
        if bin_path != j.sal.fs.pathClean(cuisine.core.replace("$BINDIR/shellinaboxd")):
            cuisine.core.file_copy(bin_path, "$BINDIR/shellinaboxd", overwrite=True)

    build(job.service, build_func)
