// ---------------------------------------------------------------------------
// Host-side sanity tests for the SIM800 AT Command & URC database
// ---------------------------------------------------------------------------

#include "sim800_at/sim800_at.hpp"
#include <cstdio>
#include <cstring>

static int g_failures = 0;

#define CHECK(cond)                                                     \
    do {                                                                \
        if (!(cond)) {                                                  \
            std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); \
            ++g_failures;                                               \
        }                                                               \
    } while (0)

static void to_lower(const char* src, char* dst, std::size_t cap) {
    std::size_t k = 0;
    for (; src[k] != '\0' && k + 1 < cap; ++k) {
        char c = src[k];
        dst[k] = (c >= 'A' && c <= 'Z') ? static_cast<char>(c + 32) : c;
    }
    dst[k] = '\0';
}

int main() {
    using namespace sim800_at;

    CHECK(total_commands() > 0);
    CHECK(total_urcs() > 0);
    CHECK(total_modules() == 9);
    CHECK(total_categories() > 0);

    for (std::size_t i = 0; i < total_commands(); ++i) {
        const ATCommand* c = &AT_COMMANDS[i];
        CHECK(find_command(c->name) == c);
        char lower[128];
        to_lower(c->name, lower, sizeof(lower));
        CHECK(find_command(lower) == c);
    }
    CHECK(find_command("ThisCommandDoesNotExist") == nullptr);
    CHECK(find_command(nullptr) == nullptr);

    for (std::size_t i = 0; i < total_urcs(); ++i) {
        const URC* u = &URCS[i];
        CHECK(find_urc(u->name) == u);
        char lower[128];
        to_lower(u->name, lower, sizeof(lower));
        if (std::strcmp(lower, u->name) != 0) {
            CHECK(find_urc(lower) == nullptr);
        }
    }
    CHECK(find_urc("+ThisURCDoesNotExist") == nullptr);
    CHECK(find_urc(nullptr) == nullptr);

    CHECK(module_index("SIM800L") == 0);
    CHECK(module_index("SIM800C-DS") == 8);
    CHECK(module_index("NotARealModule") == -1);
    CHECK(module_index("sim800l") == -1);
    CHECK(module_index(nullptr) == -1);

    CHECK(module_name_at(0) != nullptr);
    CHECK(module_name_at(999) == nullptr);

    CHECK(category_from_id("ThisCategoryDoesNotExist") == Category::INVALID);
    CHECK(category_from_id(nullptr) == Category::INVALID);
    CHECK(Category::INVALID > Category::COUNT);
    CHECK(std::strcmp(category_name(Category::INVALID), "<invalid>") == 0);
    CHECK(std::strcmp(category_name(Category::COUNT), "<count>") == 0);
    CHECK(std::strcmp(category_name(category_from_id("V25TER")), "V.25TER") == 0);

    for (std::size_t i = 0; i < total_commands(); ++i) {
        const ATCommand* c = &AT_COMMANDS[i];
        CHECK(is_command_supported(c, "sim800l") == false);
        CHECK(is_command_supported(c, "NotARealModule") == false);
    }
    CHECK(is_command_supported(nullptr, "SIM800L") == false);
    CHECK(is_command_supported(&AT_COMMANDS[0], nullptr) == false);

    for (std::size_t i = 0; i < total_urcs(); ++i) {
        const URC* u = &URCS[i];
        CHECK(is_urc_supported(u, "sim800l") == false);
        CHECK(is_urc_supported(u, "NotARealModule") == false);
    }
    CHECK(is_urc_supported(nullptr, "SIM800L") == false);
    CHECK(is_urc_supported(&URCS[0], nullptr) == false);

    {
        std::size_t count = 0;
        const ATCommand* list = commands_for_module("SIM800L", count);
        for (std::size_t i = 0; i < total_commands(); ++i) {
            if (!is_command_supported(&AT_COMMANDS[i], "SIM800L")) continue;
            bool found = false;
            for (std::size_t j = 0; j < count; ++j) {
                if (std::strcmp(list[j].name, AT_COMMANDS[i].name) == 0) {
                    found = true; break;
                }
            }
            CHECK(found);
        }
        for (std::size_t j = 0; j < count; ++j) {
            CHECK(is_command_supported(&list[j], "SIM800L"));
        }
    }
    {
        std::size_t count = 0;
        const URC* list = urcs_for_module("SIM800L", count);
        for (std::size_t i = 0; i < total_urcs(); ++i) {
            if (!is_urc_supported(&URCS[i], "SIM800L")) continue;
            bool found = false;
            for (std::size_t j = 0; j < count; ++j) {
                if (std::strcmp(list[j].name, URCS[i].name) == 0) {
                    found = true; break;
                }
            }
            CHECK(found);
        }
        for (std::size_t j = 0; j < count; ++j) {
            CHECK(is_urc_supported(&list[j], "SIM800L"));
        }
    }

    { std::size_t count = 999; (void)commands_for_module("sim800l", count);        CHECK(count == 0); }
    { std::size_t count = 999; (void)urcs_for_module("sim800l", count);            CHECK(count == 0); }
    { std::size_t count = 999; (void)commands_for_module("NotARealModule", count); CHECK(count == 0); }
    { std::size_t count = 999; (void)urcs_for_module("NotARealModule", count);     CHECK(count == 0); }
    { std::size_t count = 999; (void)commands_for_module(nullptr, count);          CHECK(count == 0); }
    { std::size_t count = 999; (void)urcs_for_module(nullptr, count);              CHECK(count == 0); }

    { std::size_t count = 999; CHECK(commands_by_category(Category::INVALID, count) == nullptr); CHECK(count == 0); }
    { std::size_t count = 999; CHECK(commands_by_category(Category::COUNT,  count) == nullptr); CHECK(count == 0); }
    { std::size_t count = 999; CHECK(urcs_by_category(Category::INVALID, count) == nullptr);     CHECK(count == 0); }
    { std::size_t count = 999; CHECK(urcs_by_category(Category::COUNT,  count) == nullptr);     CHECK(count == 0); }

    for (std::size_t i = 0; i < total_categories(); ++i) {
        Category c = static_cast<Category>(i);
        std::size_t count = 999;
        const ATCommand* r = commands_by_category(c, count);
        CHECK((r != nullptr) == (count > 0));
    }
    for (std::size_t i = 0; i < total_categories(); ++i) {
        Category c = static_cast<Category>(i);
        std::size_t count = 999;
        const URC* r = urcs_by_category(c, count);
        CHECK((r != nullptr) == (count > 0));
    }
    for (std::size_t i = 0; i < total_categories(); ++i) {
        Category c = static_cast<Category>(i);
        std::size_t count = 0;
        const ATCommand* r = commands_by_category(c, count);
        for (std::size_t j = 0; j < count; ++j) CHECK(r[j].category == c);
    }
    for (std::size_t i = 0; i < total_categories(); ++i) {
        Category c = static_cast<Category>(i);
        std::size_t count = 0;
        const URC* r = urcs_by_category(c, count);
        for (std::size_t j = 0; j < count; ++j) CHECK(r[j].category == c);
    }

    // Delta commands
    const char* kDeltaCommands[] = {
        "AT+CMIC", "AT+SIDET", "AT+CBAND",
        "AT+CSCLK", "AT+CFGRI", "AT+CHFA",
    };
    for (const char* name : kDeltaCommands) {
        CHECK(find_command(name) != nullptr);
    }

    // Chapter 21 commands
    const char* kChapter21[] = {
        "AT+SGPIO", "AT+SPWM", "AT+CANT", "AT+SD2PCM",
        "AT+SKPD", "AT+CMNRP", "AT+CEGPRS", "AT+SIMTIMER",
        "AT+SPE", "AT+CCONCINDEX", "AT+SDMODE", "AT+SRSPT",
        "AT+ECHARGE", "AT+CPCMCFG", "AT+CPCMSYNC", "AT+CBATCHK",
    };
    for (const char* name : kChapter21) {
        CHECK(find_command(name) != nullptr);
    }

    // Key commands per category
    struct CatKey { const char* cmd; const char* cat_id; };
    const CatKey kCatKeys[] = {
        { "AT+FTPGET",   "FTP" },
        { "AT+FTPPUT",   "FTP" },
        { "AT+FTPLIST",  "FTP" },
        { "AT+SMTPSEND", "Email" },
        { "AT+SMTPAUTH", "Email" },
        { "AT+POP3SRV",  "Email" },
        { "AT+CMMSSEND", "MMS" },
        { "AT+CMMSVIEW", "MMS" },
        { "AT+CMMSCURL", "MMS" },
        { "AT+CREC",     "RECORD" },
        { "AT+CTTS",     "TTS" },
        { "AT+SAPBR",    "IP" },
        { "AT+CIPPING",  "PING" },
        { "AT+CGDCONT",  "GPRS" },
        { "AT+STKTRS",   "STK" },
        { "AT+DDET",     "DDET" },
    };
    for (const auto& k : kCatKeys) {
        const ATCommand* c = find_command(k.cmd);
        CHECK(c != nullptr);
        if (c) CHECK(c->category == category_from_id(k.cat_id));
    }

    // Previously-empty categories must now be populated
    {
        const char* populated[] = {"FTP", "Email", "MMS", "RECORD", "TTS",
                                   "IP", "PING", "GPRS", "STK", "DDET"};
        for (const char* id : populated) {
            Category c = category_from_id(id);
            CHECK(c != Category::INVALID);
            std::size_t count = 0;
            (void)commands_by_category(c, count);
            CHECK(count > 0);
        }
    }

    // Two-way relation: enabled_by command must list the URC
    for (std::size_t i = 0; i < total_urcs(); ++i) {
        const URC* u = &URCS[i];
        for (std::size_t k = 0; k < u->enabled_by_count; ++k) {
            const ATCommand* c = find_command(u->enabled_by[k]);
            CHECK(c != nullptr);
            if (!c) continue;
            bool found = false;
            for (std::size_t m = 0; m < c->related_urc_count; ++m) {
                if (std::strcmp(c->related_urcs[m], u->name) == 0) {
                    found = true; break;
                }
            }
            CHECK(found);
        }
    }

    // Two-way relation: related_urc with non-empty enabled_by must list the command
    for (std::size_t i = 0; i < total_commands(); ++i) {
        const ATCommand* c = &AT_COMMANDS[i];
        for (std::size_t k = 0; k < c->related_urc_count; ++k) {
            const URC* u = find_urc(c->related_urcs[k]);
            CHECK(u != nullptr);
            if (!u) continue;
            if (u->enabled_by_count == 0) continue;
            bool found = false;
            for (std::size_t m = 0; m < u->enabled_by_count; ++m) {
                if (std::strcmp(u->enabled_by[m], c->name) == 0) {
                    found = true; break;
                }
            }
            CHECK(found);
        }
    }

    // supported_on modules must be known to the module table
    for (std::size_t i = 0; i < total_commands(); ++i) {
        const ATCommand* c = &AT_COMMANDS[i];
        for (std::size_t m = 0; m < total_modules(); ++m) {
            if (c->module_support[m]) CHECK(module_name_at(m) != nullptr);
        }
    }
    for (std::size_t i = 0; i < total_urcs(); ++i) {
        const URC* u = &URCS[i];
        for (std::size_t m = 0; m < total_modules(); ++m) {
            if (u->module_support[m]) CHECK(module_name_at(m) != nullptr);
        }
    }

    if (g_failures == 0) {
        std::printf("All AT database tests passed.\n");
        return 0;
    }
    std::printf("%d test(s) failed.\n", g_failures);
    return 1;
}
