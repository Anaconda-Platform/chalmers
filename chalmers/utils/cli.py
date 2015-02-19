import logging

from chalmers.program import Program


log = logging.getLogger(__name__)

def add_selection_group(parser):
    """
    Add program selection arguments
    """
    group = parser.add_argument_group("Select Programs")
    group.add_argument('names', nargs='*', metavar='PROG',
                        help='Names of the programs to select')
    group.add_argument('-a', '--all', action='store_true',
                        help='select all programs')


def select_programs(args, filter_paused=True):
    """
    Return a list of selected programs from command line arguments
    """

    if not (args.all ^ bool(args.names)):
        if args.all:
            log.error("You may not specify a program name when you use the -a/--all option (See -h/--help for more details)")
        else:
            log.error("You must select at least one program from the command line (See -h/--help for more details)")
        raise  SystemExit(1)

    if args.all:
        programs = Program.find_for_user()
        if filter_paused:
            programs = [prog for prog in programs if not prog.is_paused]
    else:
        programs = [Program(name) for name in args.names]
    return list(programs)

def filter_programs(programs, filt, title, name, have_filter_paused=True):
    already_in_state = [p.name for p in programs if filt(p)]

    if already_in_state:
        log.warn("The programs '%s' are already %s" % ("', '".join(already_in_state), name))

    programs = [p for p in programs if not filt(p)]

    if len(programs):
        log.info("%s programs %s" % (title, ', '.join([p.name for p in programs])))
        log.info("")
    else:
        msg = "All "
        if have_filter_paused:
            msg += "paused "
        msg += "programs already %s" % (name)
        log.warn(msg)
        raise SystemExit(0)

    return programs
