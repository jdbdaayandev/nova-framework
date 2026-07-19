# ==============================================================================
# Nova Migration Blueprint Reference
# ==============================================================================
# Column Types:
#   table.string('name', length=255)  -> VARCHAR column
#   table.text('name')                -> TEXT column
#   table.integer('name')             -> INTEGER column
#   table.boolean('name')             -> BOOLEAN column
#
# Column Modifiers:
#   .nullable()                       -> Allows NULL values
#   .unique()                         -> Enforces a UNIQUE constraint
#   .default(value)                   -> Assigns a static default value or constraint
#
# Example Chain:
#   table.string('email').unique().nullable()
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
