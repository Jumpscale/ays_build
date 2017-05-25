def init(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import ensure_container
    ensure_container(job.service, root=False)


def install(job):
    from JumpScale.baselib.atyourservice81.lib.AtYourServiceBuild import build
    import requests

    def build_func(cuisine):
        service = job.service

        cuisine.tools.sandbox.cleanup()

        tarpath = '/tmp/%s.tar.gz' % service.model.data.flistName
        # To mount the flist: sudo g8ufs -meta /tmp/meta/ -storage-url ardb://hub.gig.tech:16379 /mnt/
        # meta is the extracted flist path last parameter is the location of the moutpoint in our case /opt
        cuisine.core.run('cd %s tar -zcf %s .' % (service.model.data.sandboxPath, tarpath))
        clientid = service.model.data.clientId
        clientsecret = service.model.data.clientSecret
        response = requests.post('https://itsyou.online/v1/oauth/access_token?grant_type=client_credentials&client_id=%s&client_secret=%s&response_type=id_token' % (clientid, clientsecret))
        jwt = response.content.decode('utf-8')
        authorization = {'Authorization': 'bearer %s' % jwt}
        script = """
        import requests
        files = {'file': open('%s', 'rb')}
        requests.post('https://hub.gig.tech/upload', files=files, headers=%s)
        """ % (tarpath, authorization)
        cuisine.core.execute_python(script)

    build(job.service, build_func)


def clean(job):
    # look for build host os service
    builder_host = None
    service = job.service
    for parent in service.parents:
        if parent.model.role == 'os':
            builder_host = parent
            break
    else:
        raise j.exceptions.AYSNotFound("Can't find builder host os service")

    cuisine = builder_host.executor.cuisine
    cuisine.core.dir_remove('/mnt/building/opt')
    cuisine.core.execute_bash('docker rm -f packager cockpit portal jumpscale scality geodns php fs grafana python nodejs mongodb golang nginx shellinabox caddy influxdb redis')


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
