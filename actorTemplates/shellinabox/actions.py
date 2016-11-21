def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=True)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        cuisine.package.install('shellinabox')
        bin_path = cuisine.bash.cmdGetPath('shellinaboxd')
        cuisine.core.dir_ensure('$binDir')
        if bin_path != j.sal.fs.pathClean(cuisine.core.args_replace("$binDir/shellinaboxd")):
            cuisine.core.file_copy(bin_path, "$binDir/shellinaboxd", overwrite=True)

    build(job.service, build_func)
