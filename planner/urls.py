from django.urls import path

from .views import (
    add_daily_todo,
    add_goal,
    add_lab_goal,
    index,
    toggle_daily_todo,
    toggle_goal,
    update_goal,
)

urlpatterns = [
    path("", index, name="planner-index"),
    path("lab-goals/add/", add_lab_goal, name="planner-lab-goal-add"),
    path("daily-todos/add/", add_daily_todo, name="planner-daily-todo-add"),
    path("daily-todos/<int:todo_id>/toggle/", toggle_daily_todo, name="planner-daily-todo-toggle"),
    path("goals/add/", add_goal, name="planner-goal-add"),
    path("goals/<int:goal_id>/toggle/", toggle_goal, name="planner-goal-toggle"),
    path("goals/<int:goal_id>/update/", update_goal, name="planner-goal-update"),
]
