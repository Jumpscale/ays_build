def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        service = job.service
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

        sshkey = service.producers['sshkey'][0]
        cuisine.core.file_write("/root/.ssh/store_rsa", sshkey.model.data.keyPriv)
        cuisine.core.file_attribs('/root/.ssh/store_rsa', mode='0600')

        upload = r"""
        from JumpScale import j
        j.do.loadSSHKeys('/root/.ssh/store_rsa')
        stor_exec = j.tools.executor.getSSHBased('{store_addr}')
        stor_cuisine = j.tools.cuisine.get(stor_exec)
        ### upload to stor
        sp = stor_cuisine.tools.stor.getStorageSpace('{namespace}')
        sp.upload('{flist}', source='{source}', excludes=['/__pycache__/', '(.*)\\.pyc$', '^\/opt\/code.*'])
        """.format(
            store_addr=service.model.data.storeAddr,
            namespace=service.model.data.namespace,
            source=service.model.data.sandboxPath,
            flist=service.model.data.flistName)

        cuisine.core.execute_jumpscript(upload)

    build(job.service, build_func)


def processChange(job):
    service = job.service
    args = job.model.args

    try:
        change_category = args.pop('changeCategory')
    except KeyError:
        # changeCategory not in args. we can't decide what to do
        return

    if change_category == 'dataschema':
        for key, value in args.items():
            capnp_key = j.data.hrd.sanitize_key(key)
            setattr(service.model.data, capnp_key, value)
        service.saveAll()
