import pytest

from task import Task, TaskService, TaskStatus, TaskPriority


@pytest.fixture
def service_instance():
    """Provides a fresh TaskService instance for each test."""
    return TaskService()


class TestTaskService:
    """Test TaskService operations."""

    def test_init(self, service_instance):
        """Test service initialization."""
        assert len(service_instance.tasks) == 0
        assert service_instance.get_tasks() == []

    def test_append_task_with_auto_id(self, service_instance):
        """Test adding a single task with auto-assigned ID."""
        task = Task(name="Test task")

        service_instance.append_task(task)

        assert len(service_instance.tasks) == 1
        assert task.id == "task_1"
        assert task.index == 0

    def test_append_task_with_custom_id_and_index(self, service_instance):
        """Test adding task with custom ID and index."""
        task = Task(id="custom", name="Test task", index=5)

        service_instance.append_task(task)

        retrieved = service_instance.get_task("custom")
        assert retrieved.id == "custom"
        assert retrieved.index == 5

    def test_append_task_duplicate_id_error(self, service_instance):
        """Test error when adding duplicate ID."""
        task1 = Task(id="test", name="Task 1")
        task2 = Task(id="test", name="Task 2")

        service_instance.append_task(task1)

        with pytest.raises(ValueError, match="Task ID test already exists"):
            service_instance.append_task(task2)

    def test_append_task_duplicate_index_error(self, service_instance):
        """Test error when adding duplicate index."""
        task1 = Task(name="Task 1", index=0)
        task2 = Task(name="Task 2", index=0)

        service_instance.append_task(task1)

        with pytest.raises(ValueError, match="Index 0 is already in use"):
            service_instance.append_task(task2)

    def test_append_tasks_batch(self, service_instance):
        """Test adding multiple tasks at once."""
        tasks = [
            Task(name="Task 1"),
            Task(name="Task 2"),
            Task(name="Task 3")
        ]

        service_instance.append_tasks(tasks)

        assert len(service_instance.tasks) == 3
        all_tasks = service_instance.get_tasks()
        assert [t.name for t in all_tasks] == ["Task 1", "Task 2", "Task 3"]
        assert [t.index for t in all_tasks] == [0, 1, 2]
        assert [t.id for t in all_tasks] == ["task_1", "task_2", "task_3"]

    def test_append_tasks_with_custom_ids(self, service_instance):
        """Test batch adding with some custom IDs."""
        tasks = [
            Task(id="custom1", name="Task 1"),
            Task(name="Task 2"),
            Task(id="custom3", name="Task 3")
        ]

        service_instance.append_tasks(tasks)

        all_tasks = service_instance.get_tasks()
        assert [t.id for t in all_tasks] == ["custom1", "task_1", "custom3"]

    def test_append_tasks_duplicate_in_batch_error(self, service_instance):
        """Test error when batch contains duplicate IDs."""
        tasks = [
            Task(id="dup", name="Task 1"),
            Task(id="dup", name="Task 2")
        ]

        with pytest.raises(ValueError, match="Duplicate task ID dup found in the input list"):
            service_instance.append_tasks(tasks)

    def test_get_task(self, service_instance):
        """Test retrieving a specific task."""
        task = Task(id="test", name="Test task")
        service_instance.append_task(task)

        retrieved = service_instance.get_task("test")
        assert retrieved.name == "Test task"
        assert retrieved.id == "test"

    def test_get_task_not_found(self, service_instance):
        """Test error when task not found."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.get_task("missing")

    def test_get_tasks_sorted_by_index(self, service_instance):
        """Test getting all tasks sorted by index."""
        # Diff order
        task1 = Task(name="Task C", index=2)
        task2 = Task(name="Task A", index=0)
        task3 = Task(name="Task B", index=1)

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        tasks = service_instance.get_tasks()
        assert [t.name for t in tasks] == ["Task A", "Task B", "Task C"]
        assert [t.index for t in tasks] == [0, 1, 2]

    def test_get_tasks_by_ids(self, service_instance):
        """Test getting specific tasks by IDs."""
        task1 = Task(id="a", name="Task A")
        task2 = Task(id="b", name="Task B")
        task3 = Task(id="c", name="Task C")

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        tasks = service_instance.get_tasks_by_ids(["a", "c"])
        assert len(tasks) == 2
        assert [t.name for t in tasks] == ["Task A", "Task C"]

    def test_get_tasks_by_ids_not_found(self, service_instance):
        """Test error when getting tasks with invalid ID."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.get_tasks_by_ids(["missing"])

    def test_mark_task_as_done(self, service_instance):
        """Test marking a task as done."""
        task = Task(id="test", name="Test task")
        service_instance.append_task(task)

        service_instance.mark_task_as_done("test")

        retrieved = service_instance.get_task("test")
        assert retrieved.status == TaskStatus.DONE

    def test_mark_task_as_done_not_found(self, service_instance):
        """Test error when marking non-existent task as done."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.mark_task_as_done("missing")

    def test_mark_multiple_tasks_as_done(self, service_instance):
        """Test marking multiple tasks as done."""
        task1 = Task(id="a", name="Task A")
        task2 = Task(id="b", name="Task B")
        service_instance.append_task(task1)
        service_instance.append_task(task2)

        service_instance.mark_multiple_tasks_as_done(["a", "b"])

        assert service_instance.get_task("a").status == TaskStatus.DONE
        assert service_instance.get_task("b").status == TaskStatus.DONE

    def test_mark_multiple_tasks_as_done_partial_error(self, service_instance):
        """Test error when some tasks in batch don't exist."""
        task1 = Task(id="a", name="Task A")
        service_instance.append_task(task1)

        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.mark_multiple_tasks_as_done(["a", "missing"])

        assert service_instance.get_task("a").status == TaskStatus.TODO

    def test_mark_all_tasks_as_done(self, service_instance):
        """Test marking all tasks as done."""
        task1 = Task(id="a", name="Task A")
        task2 = Task(id="b", name="Task B")
        service_instance.append_task(task1)
        service_instance.append_task(task2)

        service_instance.mark_all_tasks_as_done()

        assert service_instance.get_task("a").status == TaskStatus.DONE
        assert service_instance.get_task("b").status == TaskStatus.DONE

    def test_update_task(self, service_instance):
        """Test updating task properties."""
        task = Task(id="test", name="Original name", priority=TaskPriority.NORMAL)
        service_instance.append_task(task)

        service_instance.update_task("test", name="Updated name", priority="high")

        retrieved = service_instance.get_task("test")
        assert retrieved.name == "Updated name"
        assert retrieved.priority == TaskPriority.HIGH

    def test_update_task_not_found(self, service_instance):
        """Test error when updating non-existent task."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.update_task("missing", name="New name")

    def test_update_task_invalid_property(self, service_instance):
        """Test error when updating invalid property."""
        task = Task(id="test", name="Test task")
        service_instance.append_task(task)

        with pytest.raises(AttributeError, match="no attribute 'invalid'"):
            service_instance.update_task("test", invalid="value")

    def test_prioritize_task(self, service_instance):
        """Test setting task priority."""
        task = Task(id="test", name="Test task")
        service_instance.append_task(task)

        service_instance.prioritize_task("test", TaskPriority.HIGH)

        retrieved = service_instance.get_task("test")
        assert retrieved.priority == TaskPriority.HIGH

    def test_prioritize_task_not_found(self, service_instance):
        """Test error when prioritizing non-existent task."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.prioritize_task("missing", TaskPriority.HIGH)

    def test_reorder_tasks(self, service_instance):
        """Test reordering tasks by swapping indices."""
        task1 = Task(id="a", name="Task A", index=0)
        task2 = Task(id="b", name="Task B", index=1)
        service_instance.append_task(task1)
        service_instance.append_task(task2)

        service_instance.reorder_tasks("a", 1)

        assert service_instance.get_task("a").index == 1
        assert service_instance.get_task("b").index == 0

    def test_reorder_tasks_same_position(self, service_instance):
        """Test reordering task to same position (no-op)."""
        task = Task(id="test", name="Test task", index=0)
        service_instance.append_task(task)

        service_instance.reorder_tasks("test", 0)

        assert service_instance.get_task("test").index == 0

    def test_reorder_tasks_not_found(self, service_instance):
        """Test error when reordering non-existent task."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.reorder_tasks("missing", 0)

    def test_reorder_tasks_invalid_target_index(self, service_instance):
        """Test error when target index doesn't exist."""
        task = Task(id="test", name="Test task", index=0)
        service_instance.append_task(task)

        with pytest.raises(ValueError, match="No task found with target index 5"):
            service_instance.reorder_tasks("test", 5)

    def test_delete_task(self, service_instance):
        """Test deleting a task."""
        task = Task(id="test", name="Test task")
        service_instance.append_task(task)

        service_instance.delete_task("test")

        assert len(service_instance.tasks) == 0
        with pytest.raises(KeyError):
            service_instance.get_task("test")

    def test_delete_task_not_found(self, service_instance):
        """Test error when deleting non-existent task."""
        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.delete_task("missing")

    def test_delete_tasks_batch(self, service_instance):
        """Test deleting multiple tasks."""
        task1 = Task(id="a", name="Task A")
        task2 = Task(id="b", name="Task B")
        task3 = Task(id="c", name="Task C")

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        service_instance.delete_tasks(["a", "c"])

        assert len(service_instance.tasks) == 1
        assert service_instance.get_task("b").name == "Task B"

    def test_delete_tasks_partial_error(self, service_instance):
        """Test error when some tasks in batch don't exist."""
        task1 = Task(id="a", name="Task A")
        service_instance.append_task(task1)

        with pytest.raises(KeyError, match="Task with ID missing not found"):
            service_instance.delete_tasks(["a", "missing"])

        assert len(service_instance.tasks) == 1
        assert service_instance.get_task("a").name == "Task A"

    def test_delete_all_tasks(self, service_instance):
        """Test deleting all tasks."""
        task1 = Task(id="a", name="Task A")
        task2 = Task(id="b", name="Task B")
        service_instance.append_task(task1)
        service_instance.append_task(task2)

        service_instance.delete_all_tasks()

        assert len(service_instance.tasks) == 0
        assert service_instance.get_tasks() == []

    def test_id_auto_increment(self, service_instance):
        """Test that auto-assigned IDs increment properly."""
        task1 = Task(name="Task 1")
        task2 = Task(name="Task 2")
        task3 = Task(name="Task 3")

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        assert task1.id == "task_1"
        assert task2.id == "task_2"
        assert task3.id == "task_3"

    def test_index_auto_increment(self, service_instance):
        """Test that auto-assigned indices increment properly."""
        task1 = Task(name="Task 1")
        task2 = Task(name="Task 2")
        task3 = Task(name="Task 3")

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        assert task1.index == 0
        assert task2.index == 1
        assert task3.index == 2

    def test_mixed_auto_and_manual_ids(self, service_instance):
        """Test mixing auto-assigned and manual IDs."""
        task1 = Task(name="Task 1")
        task2 = Task(id="manual", name="Task 2")
        task3 = Task(name="Task 3")

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        assert task1.id == "task_1"
        assert task2.id == "manual"
        assert task3.id == "task_2"

    def test_mixed_auto_and_manual_indices(self, service_instance):
        """Test mixing auto-assigned and manual indices."""
        task1 = Task(name="Task 1")
        task2 = Task(name="Task 2", index=5)
        task3 = Task(name="Task 3")

        service_instance.append_task(task1)
        service_instance.append_task(task2)
        service_instance.append_task(task3)

        assert task1.index == 0
        assert task2.index == 5
        assert task3.index == 6

        tasks = service_instance.get_tasks()
        assert [t.name for t in tasks] == ["Task 1", "Task 2", "Task 3"]
        assert [t.index for t in tasks] == [0, 5, 6]


class TestGetTaskService:
    """Test the get_task_service singleton function."""

    def test_singleton_pattern(self):
        """Test that get_task_service returns the same instance."""
        from task.service import get_task_service

        service1 = get_task_service()
        service2 = get_task_service()

        assert service1 is service2

    def test_singleton_state_persistence(self):
        """Test that singleton maintains state across calls."""
        from task.service import get_task_service

        service1 = get_task_service()
        task = Task(id="test", name="Test task")
        service1.append_task(task)

        service2 = get_task_service()
        retrieved = service2.get_task("test")

        assert retrieved.name == "Test task"
        assert len(service2.tasks) == 1
