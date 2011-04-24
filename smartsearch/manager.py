"""
This is module automatically builds
search interface for the django model.
Search interface is a django form with extra features. The
main feature is the labels which displays the number of
possible results for each option.

`SearchManger` is the main objects which stores configuration.
`SearcManager` contains one or more `Option` objects.
`Option` object is reference to model field.
`SearchForm` is enchanced Django Form which associated with
`SearchManager` instance. `SearchForm` able to build itself
using options of SearchManager.

Example of usage:
    @render_to('someapp/user_list.html')
    def some_view(request):
        sm = SearchManager(User)
        sm.add_option('sex')
        # If we pass request to the `form` method
        # then the from will be bound with `request.POST` data
        form = sm.form(request)
        # Get the queryset limited
        # to selected options
        qs = form.queryset()
        return {'qs': qs, 'manager': sm}

Layout:
    Options <--> SearchManager <--> Form <--> (SmartSearchField or any other Field)
"""
from django import forms
from django.db.models import Count
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

class SearchManager(object):
    def __init__(self, model):
        self.model = model
        self.options = []
        self._form = None
        self.col_left = None
        self.col_left_name = None
        self.col_bottom = None
        self.cols = []
        self.colnames = []

    def add_option(self, *args, **kwargs):
        Option(self, *args, **kwargs)
        
    def add_left_column(self, title, func):
        self.col_left = func
        self.col_left_name = title
    def add_bottom_column(self, func):
        self.col_bottom = func
    def add_column(self, title, func):
        self.cols.append(func)
        self.colnames.append(title)

    def form(self, request=None):
        def fixup(d):
            # Make sure every value is a list because we render some fields as non-lists.
            # Also strip jQuery's [] array notation from keys.
            ret = {}
            for k, v in d.lists():
                if k.endswith("[]"): k = k[:-2]
                ret[k] = v
            return ret
        
        if request:
            self._form = SearchForm(fixup(request.POST), manager=self)
        else:
            self._form = SearchForm(manager=self)
        return self._form
        
    def get_left_info(self, obj):
        if self.col_left == None:
            return ""
        else:
            return mark_safe("".join(["<div>" + conditional_escape(line) + "</div>" for line in self.col_left(obj).split("\n")]))
        
    def get_column_headers(self):
        return [self.col_left_name] + self.colnames
        
    def get_columns(self, obj):
        if self.cols == []:
            cols = [unicode(obj)]
        else:
            cols = [c(obj) for c in self.cols]
        
        cols[0] = mark_safe(
            "<a href=\"" + conditional_escape(obj.get_absolute_url()) + "\">"
            + conditional_escape(cols[0])
            + "</a>"
            )
        
        return cols
        
    def get_bottom_info(self, obj):
        if self.col_bottom == None:
            return ""
        else:
            return mark_safe("".join(["<div>" + conditional_escape(line) + "</div>" for line in self.col_bottom(obj).split("\n")]))
        
    def make_result(self, obj):
        left = self.get_left_info(obj)
        cols = self.get_columns(obj)
        bottom = self.get_bottom_info(obj)
        
        return mark_safe(
            "<tr valign='top'>"
            + ("<td rowspan='2'>%s</td>" % conditional_escape(left))
            + " ".join(
                [("<td>%s</td>" % conditional_escape(col)) for col in cols]
                )
            + "</tr>"
            + ("<tr><td colspan='%d'>%s</td></tr>" % (len(cols), conditional_escape(bottom)))
            )
               
    def results(self, objects):
        return "".join([self.make_result(obj) for obj in objects])

class Option(object):
    def __init__(self, manager, field_name, widget=None, required=False,
                 filter=None, choices=None):
        """
        Args:
            manager: `SearchManager` instance
            field_name: name of model's field for which the filter shoudl be built
            widget: if is not None then use that class as the field type
            required: it will be passed later to field constructor
            filter: custom logic for filtering queryset
            choices: override the choices available
        """

        self.manager = manager
        self.field_name = field_name
        self.widget = widget
        self.required = False
        self.filter = filter
        self.manager.options.append(self)
        self.choices = choices

class SearchForm(forms.Form):
    manager = None
    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager')
        smart_fields = []
        for option in self.manager.options:
            field = SmartChoiceField(self, self.manager.model, option)
            smart_fields.append(option.field_name)
            self.base_fields[option.field_name] = field
        super(SearchForm, self).__init__(*args, **kwargs)
        for field_name in smart_fields:
            field = self[field_name].field
            field.choices = list(field.generate_choices(render_counts=True))

    def queryset(self, exclude=None):
        """
        Build the `self.model` queryset limited to selected filters.
        """

        qs = self.manager.model.objects.all()

        # If form contains valid data
        if self.is_valid():
            # Then for each filter
            for option in self.manager.options:
                # If filter is not excluded explicitly
                if option.field_name != exclude:
                    # If filter contains valid data
                    if option.field_name in self.cleaned_data:
                        # Do filtering

                        if option.filter is not None:
                            qs = option.filter(qs, self)
                        else:
                            values = self.cleaned_data[option.field_name]
                            if values:
                                # Hack
                                if not isinstance(values, (list, tuple)):
                                    values = [values]
                                # if __ALL__ value presents in filter values
                                # then do not limit queryset
                                if not u'__ALL__' in values:
                                    qs = qs.filter(**{'%s__in' % option.field_name: values})
        return qs



class SmartChoiceField(forms.MultipleChoiceField):
    def __init__(self, form, model, option):
        self.meta_form = form
        self.meta_model = model
        self.meta_field_name = option.field_name
        self.meta_choices = option.choices
        
        if option.widget == None:
            option.widget = forms.CheckboxSelectMultiple
           
        changeattr = {
            forms.CheckboxSelectMultiple: "onclick",
            forms.Select: "onchange",
            forms.SelectMultiple: "onchange",
            }
        changeattr = changeattr[option.widget]
            
        if option.widget == forms.Select:
            class SelectFromMultiple(forms.Select):
                def render(self, name, value, attrs=None, choices=()):
                    return super(SelectFromMultiple, self).render(name, value[0] if value != None else None, attrs=attrs, choices=choices)
            option.widget = SelectFromMultiple
        
        super(SmartChoiceField, self).__init__(
            choices=list(self.generate_choices(render_counts=False)),
            required=option.required,
            widget=option.widget(
                attrs = { changeattr: "update_search()" })
            )

    def generate_choices(self, render_counts):
        if render_counts and not self.meta_choices:
            # Calculate number of possible results for each option, using the current
            # search terms except for this one.
            # Use `form.queryset()` to track already applied options
            # ORM explanation: do GROUP BY, then COUNT
            # http://docs.djangoproject.com/en/dev/topics/db/aggregation/#values
            resp = self.meta_form.queryset(exclude=self.meta_field_name)\
                       .values(self.meta_field_name)\
                       .annotate(_count=Count('id'))\
                       .order_by()
            counts = dict((unicode(x[self.meta_field_name]), x['_count']) for x in resp)
        elif render_counts:
            counts = {}

        if self.meta_choices:
            for key, value in self.meta_choices:
                yield (key, value)
            return

        yield ('_ALL_', 'All')
        
        def calculate_choices():
            for key, value in self.meta_model._meta.get_field(self.meta_field_name).choices:
                if render_counts:
                    count = counts.get(unicode(key), 0)
                    if count == 0:
                        continue # because we can't easily disable it
                    value = conditional_escape(value) + mark_safe(' <span class="count">(%d)</span>' % count)
                    yield (key, value, count)
                else:
                    yield (key, value, 0)

        # Sort by label (secondary sort argument)
        # Then by count (primary sort argument)
        items = sorted(calculate_choices(), key=lambda x: x[1])
        items = sorted(items, key=lambda x: x[2], reverse=True)
        for item in items:
            yield item[:2]

