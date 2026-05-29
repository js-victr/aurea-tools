"""
aurea.cli — Command-Line Interface and interactive menu for Aurea.
"""

import argparse
import sys
import time

from aurea import __version__
from aurea.core import colors, platform_info, ui
from aurea.i18n import t, get_locale
from aurea import i18n
from aurea.tools import _load_all_tools, get_tool, get_all_tools, get_tools_by_category, search_tools, CATEGORIES


def display_categories_menu():
    """Display the primary categories and shortcuts menu."""
    ui.clear_screen()
    ui.show_banner()
    
    width = platform_info.terminal_width()
    
    print(f"\n {colors.blue('■')} {colors.bold(t('ui.choose_category').upper())}\n")
    
    for idx, (cat_key, cat_i18n) in enumerate(CATEGORIES, 1):
        cat_name = t(cat_i18n)
        print(f"   {colors.green(f'[{idx}]')} {colors.bold(cat_name)}")
        
    print(f"\n {colors.blue('─' * min(width, 80))}")
    
    # Recent history
    history = ui.get_history()
    if history:
        hist_str = "  ".join([f"[{h}]" for h in history])
        print(f"  {colors.dim(t('ui.recent'))}: {colors.dim(hist_str)}")
        
    # Footers
    print(f"\n  {colors.yellow(t('ui.donate_hint')):<38}  {colors.dim('[H] Setup Guides & Help')}")
    print(f"  {colors.dim(t('ui.search_hint')):<38}  {colors.dim(t('ui.exit_hint'))}")
    print(colors.cyan("═" * min(width, 87)))


def display_category_submenu(category_key: str):
    """Display all tools inside a selected category."""
    _load_all_tools()
    cat_tools = get_tools_by_category(category_key)
    
    cat_i18n = dict(CATEGORIES)[category_key]
    ui.header(t(cat_i18n))
    
    width = platform_info.terminal_width()
    
    if not cat_tools:
        print(f"   {colors.red(t('ui.no_results'))}")
    else:
        # Desktop view (two columns)
        if width >= 85:
            col_size = (len(cat_tools) + 1) // 2
            for i in range(col_size):
                def format_item(info_obj) -> str:
                    num = info_obj.number
                    name = t(info_obj.i18n_key)
                    if len(name) > 34:
                        name = name[:32] + ".."
                    spacing = 34 - len(name)
                    return f" {colors.blue(f'[{num:>2}]')} {colors.green(name)}{' ' * max(0, spacing)}"

                esq = cat_tools[i]
                left_str = format_item(esq)
                
                if i + col_size < len(cat_tools):
                    dir_ = cat_tools[i + col_size]
                    right_str = format_item(dir_)
                else:
                    right_str = ""
                    
                print(f"  {left_str}    {right_str}")
        # Mobile view (one column)
        else:
            for info in cat_tools:
                name = t(info.i18n_key)
                print(f"  {colors.blue(f'[{info.number:>2}]')} {colors.green(name)}")
                
    print(f"\n {colors.blue('─' * min(width, 80))}")
    print(f"  {colors.dim(t('ui.back_hint')):<35}  {colors.dim(t('ui.exit_hint'))}")
    print(colors.cyan("═" * min(width, 87)))


def display_search_menu(search_query: str):
    """Display filtered tools based on user search query."""
    ui.clear_screen()
    ui.show_banner()
    
    width = platform_info.terminal_width()
    print(f"\n  {colors.yellow(t('ui.search_result', query=search_query))}\n")
    
    results = search_tools(search_query)
    for info in results:
        print(f"   [{colors.bold(info.number):>2}] {colors.green(t(info.i18n_key))} {colors.dim('(' + t(dict(CATEGORIES)[info.category]) + ')')}")
        
    if not results:
        print(f"   {colors.red(t('ui.no_results'))}")
        
    print(f"\n {colors.blue('─' * min(width, 80))}")
    print(f"  {colors.dim(t('ui.press_enter'))}")
    print(colors.cyan("═" * min(width, 87)))


def display_donation_screen():
    """Display a clean, structured support / donation screen."""
    ui.clear_screen()
    width = min(platform_info.terminal_width(), 70)
    
    top_line = "═" * width
    print(colors.cyan(f"╔{top_line}╗"))
    
    title = f" 💖 {t('ui.donation.title')} 💖 "
    padded_title = f"{title:^{width}}"
    print(f"{colors.cyan('║')}{colors.bold(colors.yellow(padded_title))}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
    
    desc1 = t('ui.donation.desc1')
    desc2 = t('ui.donation.desc2')
    print(f"{colors.cyan('║')}{colors.green(f'{desc1:^{width}}')}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{colors.green(f'{desc2:^{width}}')}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
    
    how_to = t('ui.donation.how_to')
    print(f"{colors.cyan('║')}{colors.cyan(f'{how_to:^{width}}')}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
    
    linktree_lbl = t('ui.donation.linktree')
    print(f"{colors.cyan('║')}{colors.yellow(f'{linktree_lbl:^{width}}')}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{colors.bold(f'      https://js-victr.github.io/aurea-tools/#donate':^{width})}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
    
    pix_lbl = t('ui.donation.pix')
    print(f"{colors.cyan('║')}{colors.yellow(f'{pix_lbl:^{width}}')}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{colors.bold(f'      45984313318':^{width})}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
        
    github_lbl = t('ui.donation.github')
    print(f"{colors.cyan('║')}{colors.yellow(f'{github_lbl:^{width}}')}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{colors.bold(f'      https://github.com/sponsors/js-victr':^{width})}{colors.cyan('║')}")
    print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
    
    print(colors.cyan(f"╚{top_line}╝"))
    
    ui.pause()


def display_help_menu():
    """Display the interactive Setup and Configuration Guides Knowledgebase."""
    while True:
        ui.clear_screen()
        width = min(platform_info.terminal_width(), 70)
        
        top_line = "═" * width
        print(colors.cyan(f"╔{top_line}╗"))
        title = " ⚙️  SETUP & CONFIGURATION GUIDES ⚙️ "
        print(f"{colors.cyan('║')}{colors.bold(colors.yellow(f'{title:^{width}}'))}{colors.cyan('║')}")
        print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
        
        print(f"{colors.cyan('║')}{colors.green(f'   [1] NetBox IPAM Sync Configuration':<{width})}{colors.cyan('║')}")
        print(f"{colors.cyan('║')}{colors.green(f'   [2] Multi-Vendor SSH & RouterOS API Setup':<{width})}{colors.cyan('║')}")
        print(f"{colors.cyan('║')}{colors.green(f'   [3] NetFlow v5 Exporter Router Config (MikroTik/Cisco)':<{width})}{colors.cyan('║')}")
        print(f"{colors.cyan('║')}{colors.green(f'   [4] Active Traffic Flow (Socket Tracking) Permissions':<{width})}{colors.cyan('║')}")
        print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
        print(f"{colors.cyan('║')}{colors.dim(f'   [B] Back to Main Menu':<{width})}{colors.cyan('║')}")
        print(colors.cyan(f"╚{top_line}╝"))
        
        try:
            choice = input(colors.yellow("Choose a Guide (number or [B] Back): ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
            
        if choice in ("b", ""):
            break
            
        ui.clear_screen()
        print(colors.cyan(f"╔{top_line}╗"))
        
        if choice == "1":
            print(f"{colors.cyan('║')}{colors.bold(colors.yellow(f' 1. NETBOX IPAM SYNC CONFIGURATION ':{width}))}{colors.cyan('║')}")
            print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
            
            lines = [
                "Aurea can auto-sync discovered LAN hosts and MikroTik/Cisco device",
                "interfaces directly into your NetBox IPAM instance.",
                "",
                "How to configure:",
                "1. Create a configuration file named '.aureatools.json'",
                "   in your user home directory or project root.",
                "2. Add the following JSON structure:",
                "   {",
                "       \"netbox_url\": \"https://your-netbox-instance.company.com\",",
                "       \"netbox_token\": \"your_api_token_here\"",
                "   }",
                "3. Run Tool 25 (LAN Discovery) or Tool 27 (SSH Multi-Vendor Auditor)",
                "   and choose the \"Sync to NetBox\" option to automate the upload."
            ]
            for line in lines:
                print(f"{colors.cyan('║')}{colors.green(f'  {line:<{width-2}}')}{colors.cyan('║')}")
                
        elif choice == "2":
            print(f"{colors.cyan('║')}{colors.bold(colors.yellow(f' 2. MULTI-VENDOR SSH & ROUTER API SETUP ':{width}))}{colors.cyan('║')}")
            print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
            
            lines = [
                "Aurea connects to routers, switches, and firewalls via SSH or",
                "native APIs to audit configurations and pull interfaces.",
                "",
                "Active Ports & Configuration:",
                "• MikroTik RouterOS:",
                "  - SSH: Ensure SSH is enabled ('/ip service enable ssh').",
                "  - API: Ensure RouterOS API is active on port 8728",
                "    ('/ip service enable api').",
                "• Cisco / Juniper / Huawei:",
                "  - Ensure VTY lines are configured with SSH support:",
                "    'transport input ssh'",
                "    'login local'",
                "  - Ensure user account has appropriate privilege levels (privilege 15)",
                "    to execute 'show' commands without prompt blocks."
            ]
            for line in lines:
                print(f"{colors.cyan('║')}{colors.green(f'  {line:<{width-2}}')}{colors.cyan('║')}")
                
        elif choice == "3":
            print(f"{colors.cyan('║')}{colors.bold(colors.yellow(f' 3. NETFLOW V5 ROUTER CONFIGURATION ':{width}))}{colors.cyan('║')}")
            print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
            
            lines = [
                "AureaFlow collects NetFlow v5 packets on UDP port 2055 to profile",
                "port congestion and track connections.",
                "",
                "Router Configuration Commands:",
                "",
                "• MikroTik RouterOS:",
                "  /ip traffic-flow",
                "  set enabled=yes interfaces=all",
                "  /ip traffic-flow target",
                "  add address=<Aurea_PC_IP> port=2055 version=5",
                "",
                "• Cisco IOS:",
                "  interface GigabitEthernet0/1",
                "   ip flow ingress",
                "   ip flow egress",
                "  !",
                "  ip flow-export destination <Aurea_PC_IP> 2055",
                "  ip flow-export version 5"
            ]
            for line in lines:
                print(f"{colors.cyan('║')}{colors.green(f'  {line:<{width-2}}')}{colors.cyan('║')}")
                
        elif choice == "4":
            print(f"{colors.cyan('║')}{colors.bold(colors.yellow(f' 4. ACTIVE TRAFFIC FLOW CAPABILITIES ':{width}))}{colors.cyan('║')}")
            print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
            
            lines = [
                "AureaFlow monitors active socket connections on your local machine",
                "to tag them with ASNs and carrier information in real-time.",
                "",
                "Permissions & Requirements:",
                "• Linux / macOS / Termux:",
                "  - Tracking requires raw socket capture permissions.",
                "  - Run Aurea with 'sudo' or set net capabilities on your Python binary:",
                "    'sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/python3'",
                "• Windows:",
                "  - Ensure local firewall allows outbound traffic mapping.",
                "  - Capturing outbound paths uses local netstat/ss commands."
            ]
            for line in lines:
                print(f"{colors.cyan('║')}{colors.green(f'  {line:<{width-2}}')}{colors.cyan('║')}")
                
        else:
            print(f"{colors.cyan('║')}{colors.red(f'  Invalid selection. Please choose 1-4 or B.':<{width})}{colors.cyan('║')}")
            
        print(f"{colors.cyan('║')}{' ':^{width}}{colors.cyan('║')}")
        print(colors.cyan(f"╚{top_line}╝"))
        ui.pause()


def interactive_loop():
    """Main loop for user interaction in AureaTools."""
    current_view = "categories"
    selected_category = ""
    search_query = ""
    
    while True:
        if current_view == "categories":
            display_categories_menu()
            try:
                choice = input(colors.yellow(t("ui.choose_category"))).strip()
            except (EOFError, KeyboardInterrupt):
                break
                
            if not choice:
                continue
                
            if choice == "0":
                ui.clear_screen()
                print(colors.green(t("ui.exiting")))
                break
                
            if choice.lower() == "h":
                display_help_menu()
                continue
                
            if choice.lower() == "d":
                display_donation_screen()
                continue
                
            if choice.startswith("/"):
                search_query = choice[1:].strip()
                current_view = "search"
                continue
                
            if choice in ("1", "2", "3", "4"):
                selected_category = CATEGORIES[int(choice) - 1][0]
                current_view = "submenu"
                continue
                
            # Default fallback: try to run tool number directly (for power users)
            _load_all_tools()
            tool_info = get_tool(choice)
            if tool_info and tool_info.func:
                ui.record_usage(choice)
                try:
                    tool_info.func()
                except Exception as e:
                    print(colors.red(f"\nError executing tool: {e}"))
                    ui.pause()
            else:
                print(colors.red(f"\n  {t('ui.invalid_option', option=choice, max=4)}"))
                time.sleep(1.2)
                
        elif current_view == "submenu":
            display_category_submenu(selected_category)
            try:
                choice = input(colors.yellow(t("ui.choose_submenu"))).strip()
            except (EOFError, KeyboardInterrupt):
                current_view = "categories"
                continue
                
            if not choice:
                continue
                
            if choice.lower() == "b":
                current_view = "categories"
                continue
                
            if choice == "0":
                ui.clear_screen()
                print(colors.green(t("ui.exiting")))
                break
                
            # Try to run tool
            _load_all_tools()
            tool_info = get_tool(choice)
            if tool_info and tool_info.func:
                # Double-check if the tool belongs to this category
                if tool_info.category == selected_category:
                    ui.record_usage(choice)
                    try:
                        tool_info.func()
                    except Exception as e:
                        print(colors.red(f"\nError executing tool: {e}"))
                        ui.pause()
                else:
                    print(colors.red(f"\n  A ferramenta {choice} não pertence a esta categoria."))
                    time.sleep(1.5)
            else:
                print(colors.red(f"\n  Opção inválida: '{choice}'"))
                time.sleep(1.2)
                
        elif current_view == "search":
            display_search_menu(search_query)
            try:
                choice = input(colors.yellow(t("ui.choose_or_back"))).strip()
            except (EOFError, KeyboardInterrupt):
                current_view = "categories"
                continue
                
            if not choice:
                current_view = "categories"
                continue
                
            _load_all_tools()
            tool_info = get_tool(choice)
            if tool_info and tool_info.func:
                ui.record_usage(choice)
                try:
                    tool_info.func()
                except Exception as e:
                    print(colors.red(f"\nError executing tool: {e}"))
                    ui.pause()
            else:
                current_view = "categories"


def main():
    """Main CLI entrypoint."""
    ui.protect_stdin()
    platform_info.enable_ansi_windows()

    parser = argparse.ArgumentParser(
        prog="aurea",
        description=f"Aurea v{__version__} — Advanced Network & Security Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aurea                 # Opens interactive menu
  aurea --run 8         # Directly run tool 8 (Public IP & ASN)
  aurea --list          # List all available tools
  aurea --no-color      # Disable ANSI colors
  aurea --lang pt       # Force Portuguese (BR) language
        """
    )
    parser.add_argument("--run", metavar="N", help="Run tool N directly (e.g. --run 8)")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--lang", choices=["pt", "en"], help="Force specific language (pt_BR/en_US)")
    parser.add_argument("--version", action="version", version=f"Aurea v{__version__}")
    
    args = parser.parse_args()

    # Initialize subsystems
    from aurea.core import config
    cfg = config.get_instance()
    
    # Language resolution: 1. CLI flag -> 2. Persistent preference -> 3. Autodetect
    lang_pref = cfg.get("locale", "pt_BR")
    if args.lang:
        lang_code = "pt_BR" if args.lang == "pt" else "en_US"
        cfg.set("locale", lang_code)
    else:
        lang_code = lang_pref
    i18n.init(locale_override=lang_code)
    
    # Colors resolution: 1. CLI flag -> 2. Persistent preference
    no_color_pref = cfg.get("no_color", False)
    if args.no_color:
        no_color = True
        cfg.set("no_color", True)
    else:
        no_color = no_color_pref
    colors.init(no_color=no_color)
    
    _load_all_tools()



    if args.list:
        print(f"Aurea v{__version__} — {t('ui.no_results').replace('.', '') if not get_all_tools() else 'Available tools'}:\n")
        for info in get_all_tools():
            badge = f" [{t('ui.premium_badge')}]" if info.tier == "premium" else ""
            print(f"  [{info.number:>2}] {t(info.i18n_key)}{badge}")
        return

    if args.run:
        tool_info = get_tool(args.run)
        if tool_info and tool_info.func:
            tool_info.func()
        else:
            print(f"Tool '{args.run}' not found. Use --list to see options.", file=sys.stderr)
            sys.exit(1)
        return

    # No arguments -> enter interactive menu loop
    interactive_loop()


if __name__ == "__main__":
    main()
