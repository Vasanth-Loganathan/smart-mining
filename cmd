sudo docker run --name containernet -it --rm \
  --privileged \
  --pid=host \
  --net=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/vasanthlogu/smart-mining:/smart-mining \
  containernet/containernet /bin/bash

python3 /smart-mining/smart_mining_sdn.py

sudo docker exec -it containernet /bin/bash
cd /smart-mining
python3 demo_monitor.py


sudo docker stop mn.cloud
sudo docker start mn.cloud
sudo docker exec -d mn.cloud sh -c 'cd /app && python3 app.py > /tmp/cloud.log 2>&1'