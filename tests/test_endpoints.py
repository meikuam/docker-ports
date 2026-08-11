import pytest
from app.services.containers import list_containers_data
from app.services.stats import get_stats_data


def test_containers_data():
    """Test containers data returns valid structure"""
    containers = list_containers_data()

    assert isinstance(containers, list)
    assert len(containers) > 0

    container = containers[0]

    assert "id" in container
    assert "name" in container
    assert "status" in container
    assert "ports" in container
    assert "image" in container

    assert isinstance(container["id"], str)
    assert isinstance(container["name"], str)
    assert container["status"] in ["running", "exited", "paused", "creating", "restarting", "removing", "dead"]
    assert isinstance(container["ports"], list)

    for port in container["ports"]:
        assert "container_port" in port
        assert "host_bindings" in port
        assert isinstance(port["container_port"], str)
        assert isinstance(port["host_bindings"], list)


def test_stats_data():
    """Test stats data returns valid structure"""
    stats = get_stats_data()

    assert isinstance(stats, list)
    assert len(stats) > 0

    stat = stats[0]

    assert "id" in stat
    assert "name" in stat
    assert "cpu" in stat
    assert "memory" in stat
    assert "net_input" in stat
    assert "net_output" in stat

    assert isinstance(stat["id"], str)
    assert isinstance(stat["name"], str)
    assert isinstance(stat["cpu"], (int, float))

    assert "memory" in stat
    assert isinstance(stat["memory"], (int, float))

    assert "net_input" in stat
    assert isinstance(stat["net_input"], int)

    assert "net_output" in stat
    assert isinstance(stat["net_output"], int)