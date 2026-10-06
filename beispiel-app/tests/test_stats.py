def test_status_zero_tasks(client):
    response = client.get("/api/tasks/stats")
    assert response.status_code == 200
    assert response.get_json()["total"] == 0
    assert response.get_json()["done"] == 0
    assert response.get_json()["open"] == 0
   
   
def test_status_multiple_tasks_mixed(client):
    client.post("/api/tasks", json={"title": "First Task"})
    client.post("/api/tasks", json={"title": "Second Task"})
    client.post("/api/tasks", json={"title": "Thrid Task"})
    client.put("/api/tasks/3", json={"done": True})
    response = client.get("/api/tasks/stats")
    assert response.status_code == 200
    assert response.get_json()["total"] == 3
    assert response.get_json()["done"] == 1
    assert response.get_json()["open"] == 2
    

def test_status_all_done(client):
    client.post("/api/tasks", json={"title": "First Task"})
    client.post("/api/tasks", json={"title": "Second Task"})
    client.post("/api/tasks", json={"title": "Thrid Task"})
    client.put("/api/tasks/1", json={"done": True})
    client.put("/api/tasks/2", json={"done": True})
    client.put("/api/tasks/3", json={"done": True})
    response = client.get("/api/tasks/stats")
    assert response.status_code == 200
    assert response.get_json()["total"] == 3
    assert response.get_json()["done"] == 3
    assert response.get_json()["open"] == 0