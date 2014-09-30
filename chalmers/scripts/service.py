from chalmers.windows.chalmers_service import ChalmersService

def main():
    import servicemanager
    servicemanager.Initialize(None, None)
    servicemanager.PrepareToHostSingle(ChalmersService)
    servicemanager.StartServiceCtrlDispatcher()


if __name__ == "__main__":
	main()
	