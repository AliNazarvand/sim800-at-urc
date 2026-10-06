# Public API

All functions live in namespace `sim800_at` and are declared
`inline` / `noexcept`. No allocation, no exceptions, no Arduino deps.

## Module names

### `std::size_t total_modules()`
Number of known modules. Constant `MODULE_COUNT`.

### `const char* module_name_at(std::size_t index)`
Returns module name at `index`, or `nullptr` if `index >= total_modules()`.

### `int module_index(const char* name)`
Case-sensitive lookup. Returns `-1` for `nullptr` or unknown name.

## Categories

### `std::size_t total_categories()`
Number of categories. Constant `CATEGORY_COUNT`.

### `Category category_from_id(const char* id)`
Case-insensitive lookup. Returns `Category::INVALID` on `nullptr` or unknown.

### `const char* category_name(Category c)`
Returns the category label. Returns `"<invalid>"` or `"<count>"` for the
sentinel values.

## Lookup

### `const ATCommand* find_command(const char* name)`
**Case-insensitive.** Returns `nullptr` on `nullptr` or unknown name.

### `const URC* find_urc(const char* name)`
**Case-sensitive.** Returns `nullptr` on `nullptr` or unknown name.

## Support queries

### `bool is_command_supported(const ATCommand*, const char* module)`
Returns `false` for `nullptr` arguments or unknown module.

### `bool is_urc_supported(const URC*, const char* module)`
Returns `false` for `nullptr` arguments or unknown module.

## Bulk queries

### `const ATCommand* commands_by_category(Category, std::size_t& count)`
`count` is set to 0 and `nullptr` returned for `Category::INVALID` /
`Category::COUNT`. Invariant: for every valid category `c`,
`commands_by_category(c, count)` returns non-`nullptr` iff `count > 0`.

### `const URC* urcs_by_category(Category, std::size_t& count)`
Same contract as above.

### `const ATCommand* commands_for_module(const char* module, std::size_t& count)`
**Case-sensitive** module name. Returns `nullptr`, `count = 0` for `nullptr`
or unknown module.

### `const URC* urcs_for_module(const char* module, std::size_t& count)`
Same contract as above.

## Totals

### `std::size_t total_commands()`
### `std::size_t total_urcs()`