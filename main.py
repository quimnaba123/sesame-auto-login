import clock_in
import sys
import install

def main():
    clock_in.clock_in(debug=False)
    
def force_clockout():
    import clock_out
    clock_out.clock_out(debug=False)

def create_task():
    clock_in.schedule_clock_out(debug=False)    

if __name__ == "__main__":
    """Main function with interactive prompt"""
    print("\n" + "="*50)
    print("🕒 Sesame Time Clock-In System")
    print("="*50)
    
    # Check for command line arguments first
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install" or sys.argv[1] == "-install":
            install.install_startup_task()
        elif sys.argv[1] == "--uninstall" or sys.argv[1] == "-uninstall":
            install.uninstall_startup_task()
        elif sys.argv[1] == "-force-clockout" or sys.argv[1] == "--force-clockout":
            force_clockout()
        elif sys.argv[1] == "-create-task" or sys.argv[1] == "--create-task":
            create_task()
        elif sys.argv[1] == "--help" or sys.argv[1] == "-help":
            print("\nAvailable commands:")
            print("  --install    Install startup task (runs at Windows logon)")
            print("  --uninstall  Remove startup task")
            print("  --force-clockout  Force clock-out immediately (for testing)")
            print("  --create-task  Create clock-out task for 8 hours later (for testing)")
            print("  --help       Show this help message")
            print("\nRun without arguments to clock in normally.\n")
    
    # Interactive prompt
    print("\nDo you want to start the Sesame timer now?")
    print("1) ✅ Yes, clock in now")
    print("2) ❌ No, exit")
    print("3) 🔧 Install to run automatically at startup")
    print("4) 🗑️  Uninstall startup task")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n⏰ Starting clock-in process...")
        clock_in.clock_in(debug=False)
    elif choice == "2":
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    elif choice == "3":
        install.install_startup_task()
        # Ask if they want to clock in now too
        clock_now = input("\nDo you want to clock in now as well? (y/n): ").strip().lower()
        if clock_now == 'y':
            clock_in.clock_in(debug=False)
    elif choice == "4":
        install_startup_task.uninstall_startup_task()
    else:
        print("\n❌ Invalid choice. Please run again.\n")
        sys.exit(1)

    