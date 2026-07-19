# ==============================================================================
# Nova Migration Blueprint Reference
# ==============================================================================
# Column Types:
#   table.string('name')     table.text('name')        table.integer('name')
#   table.float('name')      table.boolean('name')     table.json('name')
#   table.date('name')       table.datetime('name')
#
# Modifiers:
#   .nullable() | .unique() | .default(value)
#
# Foreign Keys:
#   table.foreignId('user_id').constrained().onDelete('cascade')
#   table.foreign('custom_id').references('id').on('roles').onUpdate('restrict')
# ==============================================================================

from engine.Database.schema import Schema

class Migration:
    def up(self):
        with Schema.create('posts') as table:
            table.id()
            # Add your custom fields here
            table.timestamps()

    def down(self):
        Schema.drop_if_exists('posts')
