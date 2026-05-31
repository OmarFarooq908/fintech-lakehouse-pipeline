{% macro surrogate_key(columns) -%}
  md5(
    {%- for column in columns -%}
      coalesce(cast({{ column }} as {{ dbt.type_string() }}), '__null__')
      {%- if not loop.last %} || '|' || {% endif -%}
    {%- endfor -%}
  )
{%- endmacro %}
