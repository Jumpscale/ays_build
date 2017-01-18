def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        # remove previous code if any
        to_clean = '$appDir/ays_bot/'
        if cuisine.core.file_exists(to_clean):
            cuisine.core.dir_remove(to_clean)

        cuisine.apps.aysbot.install(start=False, link=False)

        js_script = r"""
        from JumpScale import j
        paths = []
        paths.append("/usr/lib/python3/dist-packages")
        paths.append("/usr/lib/python3.5/")
        paths.append("/usr/local/lib/python3.5/dist-packages")
        base_dir = j.tools.cuisine.local.core.dir_paths['base']
        dest = j.sal.fs.joinPaths(base_dir, 'lib')
        excludeFileRegex = ["-tk/", "/lib2to3", "-34m-", ".egg-info", "lsb_release"]
        excludeDirRegex = ["/JumpScale", "\.dist-info", "config-x86_64-linux-gnu", "pygtk"]
        for path in paths:
            j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)
        j.tools.sandboxer.copyTo('/usr/local/bin/', '%s/bin/' % base_dir, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)
        if not j.sal.fs.exists("%s/bin/python" % base_dir):
            j.sal.fs.symlink("%s/bin/python3" % base_dir, "%s/bin/python3.5" % base_dir, overwriteTarget=True)
        j.tools.sandboxer.sandboxLibs("%s/lib" % base_dir, recursive=True)
        j.tools.sandboxer.sandboxLibs("%s/bin" % base_dir, recursive=True)
        """
        cuisine.core.execute_jumpscript(js_script)

    build(job.service, build_func)
