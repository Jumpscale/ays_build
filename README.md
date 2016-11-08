# Building of Jumpscale sandbox using AYS

Small tutorial on how to setup an AYS repository to build JumpScale sandbox

```bash
# clone repo that contains actor templates for builds
cd /opt/code/github/jumpscale
git clone https://github.com/Jumpscale/ays_build.git
# create your AYS building repo
ays create_repo -p /path/to/build/repo -g http://github.com/account/repo
cd /path/to/build/repo
# link the templates in the repo.
ln -s /opt/code/github/jumpscale/ays_build/actorTemplates/* actorTemplates/
# copy the blueprint into your repo
curl https://raw.githubusercontent.com/Jumpscale/ays_build/master/blueprint/01_build.yaml > /blueprints/01_build.yaml
# fill the blueprint to define which build host you want to use.
vim blueprints/01_build.yaml

# execute the blueprint and run
ays blueprint; ays run
```