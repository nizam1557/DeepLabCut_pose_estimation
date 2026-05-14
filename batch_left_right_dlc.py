import os
import glob
import traceback
import deeplabcut

root_folder = r"D:\Nizam\Hellen_DLC\Helens_Turning_Data\All_Turns\Multiview"

config_left = r"D:\Helene\MirrorRigTopCam1Left-Helene-2024-11-12\config.yaml"
config_right = r"D:\Helene\MirrorRigTopCam1Right-Helene-2024-11-12\config.yaml"

left_crop = [0, 482, 0, 920]
right_crop = [0, 481, 0, 920]

log_path = os.path.join(root_folder, "Batch_DLC_Left_Right_Log.txt")

done_list = []
skipped_list = []
missing_list = []
error_list = []

def has_dlc_result(outfolder):
    if not os.path.isdir(outfolder):
        return False
    csv_files = glob.glob(os.path.join(outfolder, "*DLC*.csv"))
    h5_files = glob.glob(os.path.join(outfolder, "*DLC*.h5"))
    return len(csv_files) > 0 and len(h5_files) > 0

def run_one_view(config, video_path, outfolder, crop, view_name):
    os.makedirs(outfolder, exist_ok=True)

    if has_dlc_result(outfolder):
        print(f"SKIP {view_name}: already done")
        skipped_list.append(f"{view_name}: {outfolder}")
        return

    if not os.path.exists(video_path):
        print(f"MISSING {view_name}: {video_path}")
        missing_list.append(f"{view_name}: {video_path}")
        return

    print("\n===================================")
    print(f"RUNNING {view_name}")
    print(video_path)
    print("===================================\n")

    deeplabcut.analyze_videos(
        config,
        [video_path],
        videotype="avi",
        save_as_csv=True,
        destfolder=outfolder,
        cropping=crop
    )

    deeplabcut.create_labeled_video(
        config,
        [video_path],
        videotype="avi",
        destfolder=outfolder,
        draw_skeleton=False,
        filtered=False
    )

    done_list.append(f"{view_name}: {outfolder}")

turn_folders = [
    f for f in sorted(glob.glob(os.path.join(root_folder, "*")))
    if os.path.isdir(f)
]

print(f"Found {len(turn_folders)} folders.")

for video_folder in turn_folders:
    folder_name = os.path.basename(video_folder)
    print(f"\n############ Processing folder: {folder_name} ############")

    try:
        left_video = os.path.join(video_folder, "Left_View.avi")
        right_video = os.path.join(video_folder, "Right_View.avi")

        left_outfolder = os.path.join(video_folder, "LEFT_VIEW_OUTPUT")
        right_outfolder = os.path.join(video_folder, "RIGHT_VIEW_OUTPUT")

        run_one_view(config_left, left_video, left_outfolder, left_crop, f"{folder_name} | LEFT")
        run_one_view(config_right, right_video, right_outfolder, right_crop, f"{folder_name} | RIGHT")

    except Exception as e:
        error_list.append(f"{folder_name}: {str(e)}")
        error_list.append(traceback.format_exc())

with open(log_path, "w", encoding="utf-8") as f:
    f.write("BATCH DLC LEFT + RIGHT VIEW LOG\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Root folder:\n{root_folder}\n\n")
    f.write(f"Total folders found: {len(turn_folders)}\n")
    f.write(f"Completed: {len(done_list)}\n")
    f.write(f"Skipped already done: {len(skipped_list)}\n")
    f.write(f"Missing files: {len(missing_list)}\n")
    f.write(f"Errors: {len(error_list)}\n\n")

    f.write("\nCOMPLETED\n")
    f.write("-" * 60 + "\n")
    for item in done_list:
        f.write(item + "\n")

    f.write("\nSKIPPED ALREADY DONE\n")
    f.write("-" * 60 + "\n")
    for item in skipped_list:
        f.write(item + "\n")

    f.write("\nMISSING FILES\n")
    f.write("-" * 60 + "\n")
    for item in missing_list:
        f.write(item + "\n")

    f.write("\nERRORS\n")
    f.write("-" * 60 + "\n")
    for item in error_list:
        f.write(item + "\n")

print("\n===================================")
print("BATCH PROCESSING DONE")
print("Log saved here:")
print(log_path)
print("===================================\n")