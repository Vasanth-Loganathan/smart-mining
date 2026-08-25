from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel


def run():

    net = Containernet(controller=Controller)

    # =====================================================
    # SDN CONTROLLER
    # =====================================================

    net.addController(
        'c0',
        controller=Controller,
        ip='127.0.0.1',
        port=6653
    )

    # =====================================================
    # APPLICATION CONTAINERS
    # =====================================================

    sensor = net.addDocker(
        'sensor',
        dimage='smart-mining-sensor',
        ip='10.0.1.10/24',
        cmd='python sensor_simulator.py'
    )

    edge = net.addDocker(
        'edge',
        dimage='smart-mining-edge',
        ip='10.0.1.20/24',
        cmd='python app.py'
    )

    fog = net.addDocker(
        'fog',
        dimage='smart-mining-fog',
        ip='10.0.2.30/24',
        cmd='python app.py'
    )

    cloud = net.addDocker(
        'cloud',
        dimage='smart-mining-cloud',
        ip='10.0.3.40/24',
        cmd='python app.py'
    )

    # =====================================================
    # SDN SWITCHES
    # =====================================================

    s1 = net.addSwitch(
        's1',
        failMode='standalone'
    )

    s2 = net.addSwitch(
        's2',
        failMode='standalone'
    )

    s3 = net.addSwitch(
        's3',
        failMode='standalone'
    )

    # =====================================================
    # TOPOLOGY
    # =====================================================

    # Sensor <-> Edge
    net.addLink(sensor, s1)
    net.addLink(edge, s1)

    # Edge <-> Fog
    net.addLink(edge, s2)
    net.addLink(fog, s2)

    # Fog <-> Cloud
    net.addLink(fog, s3)
    net.addLink(cloud, s3)

    # =====================================================
    # START NETWORK
    # =====================================================

    net.start()

    # =====================================================
    # BRING INTERFACES UP
    # =====================================================

    sensor.cmd(
        'ip link set sensor-eth0 up'
    )

    edge.cmd(
        'ip link set edge-eth0 up'
    )

    edge.cmd(
        'ip link set edge-eth1 up'
    )

    fog.cmd(
        'ip link set fog-eth0 up'
    )

    fog.cmd(
        'ip link set fog-eth1 up'
    )

    cloud.cmd(
        'ip link set cloud-eth0 up'
    )

    # =====================================================
    # SECOND INTERFACE IP ADDRESSES
    # =====================================================

    edge.cmd(
        'ip addr add 10.0.2.20/24 '
        'dev edge-eth1'
    )

    fog.cmd(
        'ip addr add 10.0.3.30/24 '
        'dev fog-eth1'
    )

    # =====================================================
    # ENABLE IP FORWARDING
    # =====================================================

    edge.cmd(
        'echo 1 > /proc/sys/net/ipv4/ip_forward'
    )

    fog.cmd(
        'echo 1 > /proc/sys/net/ipv4/ip_forward'
    )

    # =====================================================
    # SENSOR ROUTING
    # =====================================================

    sensor.cmd(
        'ip route del default'
    )

    sensor.cmd(
        'ip route add default '
        'via 10.0.1.20 '
        'dev sensor-eth0'
    )

    # =====================================================
    # EDGE ROUTING
    # =====================================================

    edge.cmd(
        'ip route add 10.0.3.0/24 '
        'via 10.0.2.30 '
        'dev edge-eth1'
    )

    # =====================================================
    # FOG ROUTING
    # =====================================================

    fog.cmd(
        'ip route add 10.0.1.0/24 '
        'via 10.0.2.20 '
        'dev fog-eth0'
    )

    # =====================================================
    # CLOUD ROUTING
    # =====================================================

    cloud.cmd(
        'ip route add 10.0.1.0/24 '
        'via 10.0.3.30 '
        'dev cloud-eth0'
    )

    cloud.cmd(
        'ip route add default '
        'via 10.0.3.30 '
        'dev cloud-eth0'
    )

    # =====================================================
    # INFORMATION
    # =====================================================

    print()
    print("==============================================")
    print("       SMART MINING SDN NETWORK")
    print("==============================================")
    print()

    print("Sensor : 10.0.1.10")
    print("Edge   : 10.0.1.20 / 10.0.2.20")
    print("Fog    : 10.0.2.30 / 10.0.3.30")
    print("Cloud  : 10.0.3.40")

    print()
    print("Topology:")
    print(
        "Sensor -- s1 -- Edge -- s2 -- Fog -- s3 -- Cloud"
    )

    print()
    print("Applications:")
    print("Edge  : 10.0.1.20:5000")
    print("Fog   : 10.0.2.30:5000")
    print("Cloud : 10.0.3.40:5000")

    print()
    print("==============================================")
    print()

    CLI(net)

    net.stop()


if __name__ == '__main__':

    setLogLevel('info')

    run()