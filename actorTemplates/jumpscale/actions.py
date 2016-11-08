def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build
    service = job.service

    def build_func(cuisine):
        cuisine.core.dir_remove('$codeDir/github/jumpscale/jumpscale_core8')
        cuisine.development.js8.install(deps=False, keep=True, reset=True, branch=service.model.data.branch)


        # replace symbolic link with actual file
        directories = [cuisine.core.dir_paths['binDir'], cuisine.core.dir_paths['libDir']]
        skip = ['npm']
        for directory in directories:
            links = cuisine.core.fs_find(directory, type='l')
            for link in links:
                if link in skip:
                    continue
                _, dest, _ = cuisine.core.run('readlink {}'.format(link), showout=False)
                cuisine.core.run('rm {link}; cp -rv {dest} {link}'.format(link=link, dest=dest))

        # copy binaries that are left on the system into the sandbox
        jspython_path = cuisine.core.command_location('jspython')
        if cuisine.core.file_exists('$binDir/jspython'):
            cuisine.core.file_unlink('$binDir/jspython')
        cuisine.core.file_copy(jspython_path, '$binDir/jspython')
        script = r"""cd /opt/jumpscale8/bin
    cp /usr/local/bin/bro .
    cp /usr/bin/tarantool* .
    cp /usr/bin/lua* .
    cp /usr/local/bin/capnp* .
    cp /usr/local/lib/luarocks/rocks/lua-capnproto/0.1.3-1/bin/* .
    cp /usr/local/lib/luarocks/rocks/lua-cjson/2.1.0-1/bin/* .
    cp /usr/local/lib/libluajit-5.1.so .
    cp /usr/local/lib/lua/5.1/* .
    rsync -rv /usr/local/share/lua/5.1/ /opt/jumpscale8/lib/lua/
    rsync -rv /usr/local/share/luajit-2.1.0-beta2/ /opt/jumpscale8/lib/lua/
    mkdir -p /opt/jumpscale8/lib/lua/luarocks/
    rsync -rv /usr/share/lua/5.1/luarocks/ /opt/jumpscale8/lib/lua/luarocks/
    mkdir -p /opt/jumpscale8/lib/lua/tarantool/
    rsync -rv /usr/share/tarantool/ /opt/jumpscale8/lib/lua/tarantool/"""
        cuisine.core.execute_bash(script)

        cuisine.tools.sandbox.cleanup()
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
