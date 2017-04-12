def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build
    service = job.service

    def build_func(cuisine):
        cuisine.solutions.cockpit.install(start=False, branch=service.model.data.branch, production=False)

        # replace symbolic link with actual file
        directories = [cuisine.core.replace('$JSAPPSDIR/atyourservice'), cuisine.core.replace('$JSAPPSDIR/portals/')]
        for directory in directories:
            links = cuisine.core.find(directory, type='l')
            for link in links:
                _, dest, _ = cuisine.core.run('readlink -f {}'.format(link), showout=False)
                cuisine.core.run('rm {link}; cp -rv {dest} {link}'.format(link=link, dest=dest))

        js_script = r"""
        from JumpScale import j
        paths = []
        paths.append("/usr/lib/python3/dist-packages")
        paths.append("/usr/lib/python3.5/")
        paths.append("/usr/local/lib/python3.5/dist-packages")
        base_dir = j.tools.cuisine.local.core.dir_paths['JSBASEDIR']
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
