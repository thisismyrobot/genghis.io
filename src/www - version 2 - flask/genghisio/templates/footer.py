
    # Check we have at least one behaviour
    if len(__behaviours) == 0:
        raise Exception(
            'At least one method must have a behaviour decorator - eg:\n' + \
            '<EXAMPLE>\n' + \
            '@behaviour(priority=1)\n' + \
            'def hello_world():\n' + \
            '    ...\n' + \
            '</EXAMPLE>\n' + \
            'Here the \'hello_world\' method has a behaviour decorator. ' + \
            'The decorator is placed on the line directly above the ' + \
            'method declaration.')

    # Record the behaviour priorities
    __output['behaviours'] = __behaviours

    # Create a robot
    r = RunnableRobot()

    def called_behav_except(called):
        raise Exception(
            'It looks like you are trying to call the ' + \
            '\'' + called + '\' behaviour method from the either another ' + \
            'behaviour method or a helper.\n\n' + \
            'This is not allowed as behaviours are called automatically.')

    # Call the behaviours
    for behav_func in __behaviours.keys():
        if behav_func not in __BLACKLIST:
            try:
                getattr(r, behav_func)()
            except NameError as ne:
                # Catch calls between behaviours and offer help
                for called_behav_func in __behaviours.keys():
                    if called_behav_func in ne.message:
                        called_behav_except(called_behav_func)
                raise

# Finish off the try-except
except Exception as ex:
    __expt = ex

# Add any exceptions to the output json for display
if __expt is not None:
    import traceback
    __output['errors'] = traceback.format_exc()

# Add the memory to the output to save it
__output['memory'] = memory.for_upload

# Return the output json object
sys.stdout.write(json.dumps(__output))
