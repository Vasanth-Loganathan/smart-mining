sudo docker run --name containernet -it --rm \
  --privileged \
  --pid=host \
  --net=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/vasanthlogu/smart-mining:/smart-mining \
  containernet/containernet /bin/bash

python3 /smart-mining/smart_mining_sdn.py

