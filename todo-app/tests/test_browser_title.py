"""Tests for browser tab title with todo count."""

import pytest

from app.database import Todo, TodoList, User


class TestBrowserTitle:
    """Tests for browser tab title functionality."""

    def test_title_shows_count_with_incomplete_todos(self, authenticated_client, test_list, db_session):
        """Test that browser title shows count when there are incomplete todos."""
        # Create some todos
        todo1 = Todo(list_id=test_list.id, title="Todo 1", is_completed=False, position=0)
        todo2 = Todo(list_id=test_list.id, title="Todo 2", is_completed=False, position=1)
        todo3 = Todo(list_id=test_list.id, title="Todo 3", is_completed=True, position=2)
        db_session.add_all([todo1, todo2, todo3])
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        # Should show 2 incomplete todos in title
        assert b"<title>(2) Test List - Todo App</title>" in response.content

    def test_title_no_count_when_all_complete(self, authenticated_client, test_list, db_session):
        """Test that browser title does not show count when all todos are complete."""
        # Create completed todos
        todo1 = Todo(list_id=test_list.id, title="Todo 1", is_completed=True, position=0)
        todo2 = Todo(list_id=test_list.id, title="Todo 2", is_completed=True, position=1)
        db_session.add_all([todo1, todo2])
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        # Should not show count in title
        assert b"<title>Test List - Todo App</title>" in response.content
        assert b"(0)" not in response.content

    def test_title_no_count_when_list_empty(self, authenticated_client, test_list, db_session):
        """Test that browser title does not show count when list is empty."""
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        # Should not show count in title
        assert b"<title>Test List - Todo App</title>" in response.content

    def test_title_updates_in_data_attribute(self, authenticated_client, test_list, db_session):
        """Test that the data-incomplete-count attribute is set correctly."""
        # Create some todos
        todo1 = Todo(list_id=test_list.id, title="Todo 1", is_completed=False, position=0)
        todo2 = Todo(list_id=test_list.id, title="Todo 2", is_completed=True, position=1)
        db_session.add_all([todo1, todo2])
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        # Check that the data attribute is set with the count
        assert b'data-incomplete-count="1"' in response.content

    def test_toggle_todo_returns_count_oob(self, authenticated_client, test_todo, db_session):
        """Test that toggling a todo returns the updated count via OOB swap."""
        response = authenticated_client.patch(f"/api/todos/{test_todo.id}/toggle")
        assert response.status_code == 200
        # Check that OOB update includes the count
        assert b"hx-swap-oob" in response.content
        # The count element should be present
        assert test_todo.list_id.encode() in response.content

    def test_create_todo_returns_count_oob(self, authenticated_client, test_list, db_session):
        """Test that creating a todo returns the updated count via OOB swap."""
        response = authenticated_client.post(
            "/api/todos",
            data={
                "list_id": test_list.id,
                "title": "New Todo",
            },
        )
        assert response.status_code == 200
        # Check that OOB update includes the count
        assert b"hx-swap-oob" in response.content

    def test_delete_todo_returns_count_oob(self, authenticated_client, test_todo, db_session):
        """Test that deleting a todo returns the updated count via OOB swap."""
        response = authenticated_client.delete(f"/api/todos/{test_todo.id}")
        assert response.status_code == 200
        # Check that OOB update includes the count
        assert b"hx-swap-oob" in response.content
        assert b"list-content-count-updater" in response.content
