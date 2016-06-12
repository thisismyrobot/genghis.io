def _add(existing, key, value, priority, behaviour):
    """ Adds a (key, value, priority, behaviour) tuple to the 'existing' list
        of controls, taking into account the priority of the key-value pair
        that you are passing in.
    """
    data = [key, value, priority, behaviour]
    if len(existing) == 0:
        return [data]

    # Insert the new occurance
    for i in range(len(existing)):
        if existing[i][2] > priority:
            existing.insert(i, data)
            return existing

    existing.append(data)
    return existing


def update(controls_queue, new_controls, behaviours):
    """ Pass the existing, and new, controls and this will return an updated
        controls queue.
    """
    # Create a new list to work with, containing the old controls
    try:
        updated_controls_queue = list(controls_queue)

        # Add the controls one by one
        for (key, value, behaviour) in new_controls:
            try:
                priority = int(behaviours[behaviour])
            except KeyError:
                # Only happens if behaviour is not in mapping, but is in
                # controls - this "shouldn't happen"...
                continue
            updated_controls_queue = _add(
                updated_controls_queue, key, value, priority, behaviour)

        return updated_controls_queue

    except:
        # Should only happen if there's some sort of corruption in memcache...
        return []
