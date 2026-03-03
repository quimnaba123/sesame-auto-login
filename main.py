import clock_in
import sys

def main():
    clock_in.clock_in(debug=False)
    
def force_clockout():
    import clock_out
    clock_out.clock_out(debug=False)    

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-force-clockout":
        force_clockout()
    else:
        main()