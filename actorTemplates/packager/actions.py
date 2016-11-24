def init(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.AtYourServiceBuild import build

    def build_func(cuisine):
        service = job.service

        cuisine.tools.sandbox.cleanup()

        cuisine.apps.ipfs.install(reset=Flase)
        cuisine.apps.ipfs.start(name='main')

        upload = r"""
        from JumpScale import j
        source = '{source}'
        outlist = "/tmp/{flist}"
        backend = '/mnt/flist_upload'
        flist = j.tools.flist.get_flist()
        archiver = j.tools.flist.get_archiver()

        n = flist.build(source, excludes=['/__pycache__/', '(.*)\\.pyc$', '^\/opt\/code.*'])
        print("%d items added" % n)

        archiver.build(flist, backend)

        data = flist.dumps(source)

        with open(outlist, "w") as output:
            output.write(data)

        final = archiver.push_to_ipfs(outlist)
        flist_url = "https://ipfs.io/ipfs/%s" % final
        print(flist_url)
        """.format(
            source=service.model.data.sandboxPath,
            flist=service.model.data.flistName)

        rc, out = cuisine.core.execute_jumpscript(upload)
        if rc == 0:
            flist_url = out.strip().splitlines()[0]
            print("flist url : %s" % flist_url)
            service.model.data.flistURL = flist_url
            service.saveAll()
        else:
            raise j.exceptions.RuntimeError("Error during sandboxing: %s" % out)

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
