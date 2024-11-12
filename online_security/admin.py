# online_security/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Category, Recommendation, Solution, Tutorial, TutorialStep
from .management.commands.populate_online_security_data import SecurityDataAdmin

class TutorialStepInline(admin.TabularInline):
    model = TutorialStep
    extra = 1
    fields = ['order', 'name', 'description', 'image_file', 'notes']
    ordering = ['order']

class TutorialInline(admin.TabularInline):
    model = Tutorial
    extra = 1
    fields = ['name', 'description', 'estimated_time', 'difficulty', 'order']
    ordering = ['order']

class RecommendationInline(admin.TabularInline):
    model = Recommendation.categories.through
    extra = 1

class SolutionInline(admin.TabularInline):
    model = Solution.recommendations.through
    extra = 1

@admin.register(Category)
class CategoryAdmin(SecurityDataAdmin, admin.ModelAdmin):
    list_display = ['name', 'importance', 'order', 'recommendation_count']
    list_filter = ['importance']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    inlines = [RecommendationInline]
    actions = ['move_up', 'move_down']

    def recommendation_count(self, obj):
        return obj.recommendations.count()
    recommendation_count.short_description = 'Recommendations'

    def move_up(self, request, queryset):
        for obj in queryset:
            if obj.order > 1:
                obj.update_order(obj.order - 1)
    move_up.short_description = "Move selected items up"

    def move_down(self, request, queryset):
        max_order = Category.objects.all().aggregate(models.Max('order'))['order__max']
        for obj in queryset:
            if obj.order < max_order:
                obj.update_order(obj.order + 1)
    move_down.short_description = "Move selected items down"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'populate-security-data/',
                self.admin_site.admin_view(self.populate_security_data_view),
                name='populate_security_data',
            ),
        ]
        return custom_urls + urls

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['name', 'importance', 'order', 'category_list', 'solution_count']
    list_filter = ['importance', 'categories']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    filter_horizontal = ['categories']
    inlines = [SolutionInline]
    actions = ['move_up', 'move_down']

    def category_list(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    category_list.short_description = 'Categories'

    def solution_count(self, obj):
        return obj.solutions.count()
    solution_count.short_description = 'Solutions'

    def move_up(self, request, queryset):
        for obj in queryset:
            if obj.order > 1:
                obj.update_order(obj.order - 1)
    move_up.short_description = "Move selected items up"

    def move_down(self, request, queryset):
        max_order = Recommendation.objects.all().aggregate(models.Max('order'))['order__max']
        for obj in queryset:
            if obj.order < max_order:
                obj.update_order(obj.order + 1)
    move_down.short_description = "Move selected items down"

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'type', 
        'cost_display', 
        'implementation_difficulty',
        'learning_curve',
        'platform_list',
        'order'
    ]
    list_filter = ['type', 'implementation_difficulty', 'learning_curve', 'cost_duration']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    filter_horizontal = ['recommendations']
    inlines = [TutorialInline]
    actions = ['move_up', 'move_down']

    def cost_display(self, obj):
        if obj.cost:
            return f"${obj.cost} ({obj.get_cost_duration_display()})"
        return "Free"
    cost_display.short_description = 'Cost'

    def platform_list(self, obj):
        if obj.supported_platforms:
            return ", ".join(obj.supported_platforms)
        return "All Platforms"
    platform_list.short_description = 'Supported Platforms'

    def move_up(self, request, queryset):
        for obj in queryset:
            if obj.order > 1:
                obj.update_order(obj.order - 1)
    move_up.short_description = "Move selected items up"

    def move_down(self, request, queryset):
        max_order = Solution.objects.all().aggregate(models.Max('order'))['order__max']
        for obj in queryset:
            if obj.order < max_order:
                obj.update_order(obj.order + 1)
    move_down.short_description = "Move selected items down"

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ['name', 'solution', 'difficulty', 'estimated_time', 'step_count', 'order']
    list_filter = ['difficulty', 'solution']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    inlines = [TutorialStepInline]
    actions = ['move_up', 'move_down']

    def step_count(self, obj):
        return obj.steps.count()
    step_count.short_description = 'Steps'

    def move_up(self, request, queryset):
        for obj in queryset:
            if obj.order > 1:
                obj.update_order(obj.order - 1)
    move_up.short_description = "Move selected items up"

    def move_down(self, request, queryset):
        max_order = Tutorial.objects.all().aggregate(models.Max('order'))['order__max']
        for obj in queryset:
            if obj.order < max_order:
                obj.update_order(obj.order + 1)
    move_down.short_description = "Move selected items down"

@admin.register(TutorialStep)
class TutorialStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'tutorial', 'order', 'has_image']
    list_filter = ['tutorial']
    search_fields = ['name', 'description']
    ordering = ['tutorial', 'order']
    actions = ['move_up', 'move_down']

    def has_image(self, obj):
        return bool(obj.image_file)
    has_image.boolean = True
    has_image.short_description = 'Has Image'

    def move_up(self, request, queryset):
        for obj in queryset:
            if obj.order > 1:
                obj.update_order(obj.order - 1)
    move_up.short_description = "Move selected items up"

    def move_down(self, request, queryset):
        max_order = TutorialStep.objects.all().aggregate(models.Max('order'))['order__max']
        for obj in queryset:
            if obj.order < max_order:
                obj.update_order(obj.order + 1)
    move_down.short_description = "Move selected items down"