def parse_output(output):
    # Converts each output line to a dictionary for processing
    vessel_data = []
    for line in output:
        vessel_id, rest = line.split(":")
        berth_range, time_range, crane_list = rest.split(";")

        # Parse berth range
        berth_start, berth_end = map(int, berth_range.split("-"))

        # Parse time range
        time_start, time_end = map(int, time_range.split(".."))

        # Parse crane list, handling the case where no cranes are provided
        cranes = list(map(int, crane_list.strip("[]").split(","))) if crane_list.strip("[]") else []

        vessel_data.append({
            "vessel_id": int(vessel_id),
            "berth_start": berth_start,
            "berth_end": berth_end,
            "time_start": time_start,
            "time_end": time_end,
            "cranes": cranes
        })
    return vessel_data


def check_constraints(vessel_data, min_safety_distance, crane_base_positions, crane_range, max_shift_hours,
                      minimumnumqcs):
    results = {"non_overlapping_berths": True, "time_overlap": True, "crane_assignments": True}

    # Check each vessel against others for berth and time overlaps
    for i, vessel in enumerate(vessel_data):
        for j, other_vessel in enumerate(vessel_data):
            if i >= j:
                continue  # Avoid redundant checks

            # Check if berth ranges overlap
            berth_overlap = not (
                        vessel["berth_end"] <= other_vessel["berth_start"] or vessel["berth_start"] >= other_vessel[
                    "berth_end"])
            # Check if time ranges overlap
            time_overlap = not (
                        vessel["time_end"] <= other_vessel["time_start"] or vessel["time_start"] >= other_vessel[
                    "time_end"])

            # If both berth and time overlap, update the results
            if berth_overlap and time_overlap:
                results["non_overlapping_berths"] = False  # They are overlapping
                results["time_overlap"] = False  # They overlap in time

        # Check crane assignments
        assigned_cranes = vessel["cranes"]
        min_required_cranes = minimumnumqcs[vessel["vessel_id"] - 1]  # Assuming vessel IDs are 1-indexed

        # Check if the minimum number of cranes is met
        if len(assigned_cranes) < min_required_cranes:
            results["crane_assignments"] = False

        for crane in assigned_cranes:
            # Ensure crane index is within range of crane_base_positions
            if 1 <= crane <= len(crane_base_positions):
                crane_position = crane_base_positions[crane - 1]
                # Check if the crane can cover the vessel's berth range
                if not (crane_position <= vessel["berth_start"] < vessel["berth_end"] <= crane_position + crane_range):
                    results["crane_assignments"] = False
            else:
                print(f"Warning: Crane ID {crane} for vessel {vessel['vessel_id']} is out of range.")
                results["crane_assignments"] = False

    return results


# Example output
output = [
    "1:248-448;33..57;[3, 4, 6, 7, 8]",
"2:559-626;138..4;[8, 9, 13, 14, 15, 18, 19]",
"3:529-599;83..107;[11, 17]",
"4:301-372;114..129;[2, 3]",
"5:752-822;107..155;[16, 17]",
"6:458-630;35..62;[9, 10, 11, 12, 13, 14, 15]",
"7:280-421;70..90;[1, 2, 3, 4, 5, 6, 7, 8, 9]",
"8:711-787;20..40;[16, 18]",
"9:390-479;9..33;[3, 4, 5, 6, 8, 11, 12, 13]",
"10:797-950;32..67;[19, 20]",
"11:832-950;123..155;[19, 20]",
"12:183-291;121..145;[1, 4]",
"13:517-597;7..31;[7, 9, 10, 14, 15, 17]",
"14:50-238;7..63;[1, 2]",
"15:533-685;114..150;[10, 13, 14, 15, 18]",
"16:640-787;40..78;[16, 17, 18]",
"17:382-523;107..143;[5, 6, 7, 8, 9, 11, 12]",
"18:608-684;8..32;[19, 20]",
"19:609-685;89..113;[10, 13, 14, 15, 18, 19, 20]",
"20:483-630;62..78;[10, 11, 12, 13, 14, 15]",
]

# Parameters
min_safety_distance = 10  # example minimum safety distance in meters
crane_base_positions = [21,50,79,109,138,168,197,226,256,285,315,344,374,403,432,462,491,521,550,580]  # example crane base positions
crane_range = 400  # example crane range in meters
max_shift_hours = 4  # example max shift for flexible berthing
minimumnumqcs = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]  # Minimum number of cranes required for each vessel

# Run checks
vessel_data = parse_output(output)
results = check_constraints(vessel_data, min_safety_distance, crane_base_positions, crane_range, max_shift_hours,
                            minimumnumqcs)

print("Constraint Checks:", results)
