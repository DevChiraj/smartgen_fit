import os
import shutil
import pandas as pd
import json

# --- ගොනු පිහිටීම් (File Paths) ---
raw_dir = "raw_dataset"

# 1. Hugging Face
hf_csv_path = os.path.join(raw_dir, "body.csv")

# 2. Kaggle 1
kaggle_dir = os.path.join(raw_dir, "kaggle_data")
kaggle_csv_path = os.path.join(kaggle_dir, "Body Measurements Image Dataset.csv")

# 3. අලුත් Dataset 3
dataset3_dir = os.path.join(raw_dir, "dataset3", "Images_Blurred")
dataset3_csv_path = os.path.join(raw_dir, "dataset3", "measurements_2.csv")

out_dir = "datasets/body_images"
labels_out_path = os.path.join(out_dir, "labels.csv")


# --- JSON වලින් දත්ත ගැනීමේ ශ්‍රිතය (Hugging Face සඳහා) ---
def extract_value(d, keyword):
    for k, v in d.items():
        if isinstance(v, dict):
            res = extract_value(v, keyword)
            if res is not None:
                return res
        elif isinstance(k, str) and keyword in k.lower():
            try:
                if isinstance(v, str):
                    v = "".join(c for c in v if c.isdigit() or c == ".")
                return float(v)
            except ValueError:
                pass
    return None


def prepare_dataset():
    # පරණ ෆෝල්ඩර මකා අලුත් ෆෝල්ඩර සෑදීම
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    for category in ["thin", "normal", "overweight"]:
        os.makedirs(os.path.join(out_dir, category), exist_ok=True)

    labels_data = []
    copied_count = 0

    # ==========================================
    # කොටස A: Hugging Face Dataset එක
    # ==========================================
    print("Hugging Face දත්ත සකසමින් පවතී...")
    try:
        hf_df = pd.read_csv(hf_csv_path)
        for index, row in hf_df.iterrows():
            front_rel_path = str(row["front"]).replace("\\", "/").replace("/", os.sep)
            json_rel_path = (
                str(row["measurements"]).replace("\\", "/").replace("/", os.sep)
            )

            src_img = os.path.join(raw_dir, front_rel_path)
            json_path = os.path.join(raw_dir, json_rel_path)
            set_id = str(row["front"]).replace("\\", "/").split("/")[1]

            if os.path.exists(src_img) and os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    measurements = json.load(f)

                height_cm = extract_value(measurements, "height")
                weight_kg = extract_value(measurements, "weight")

                if height_cm and weight_kg:
                    height_m = height_cm / 100.0
                    bmi = round(weight_kg / (height_m**2), 2)
                    category = (
                        "thin"
                        if bmi < 18.5
                        else "normal" if bmi < 25.0 else "overweight"
                    )

                    new_img_name = f"hf_{set_id}_front_img.jpg"
                    dst_img = os.path.join(out_dir, category, new_img_name)
                    shutil.copy2(src_img, dst_img)

                    labels_data.append(
                        {
                            "subject_id": f"hf_{set_id}",
                            "source_image": src_img,
                            "dest_image": dst_img,
                            "height_cm": height_cm,
                            "weight_kg": weight_kg,
                            "bmi": bmi,
                            "body_type": category,
                            "dataset_source": "hugging_face",
                        }
                    )
                    copied_count += 1
    except Exception as e:
        print(f"Hugging Face දෝෂයකි: {e}")

    # ==========================================
    # කොටස B: Kaggle Dataset එක
    # ==========================================
    print("\nKaggle දත්ත සකසමින් පවතී...")
    try:
        kaggle_df = pd.read_csv(kaggle_csv_path)
        for index, row in kaggle_df.iterrows():
            set_id = str(row["set_id"])

            src_img_jpg = os.path.join(kaggle_dir, set_id, "front_img.jpg")
            src_img_png = os.path.join(kaggle_dir, set_id, "front_img.png")
            src_img_jpeg = os.path.join(kaggle_dir, set_id, "front_img.jpeg")

            src_img = (
                src_img_jpg
                if os.path.exists(src_img_jpg)
                else (
                    src_img_png
                    if os.path.exists(src_img_png)
                    else src_img_jpeg if os.path.exists(src_img_jpeg) else None
                )
            )

            if src_img:
                height_cm = float(row["height"])
                weight_kg = float(row["weight"])

                height_m = height_cm / 100.0
                bmi = round(weight_kg / (height_m**2), 2)
                category = (
                    "thin" if bmi < 18.5 else "normal" if bmi < 25.0 else "overweight"
                )

                ext = os.path.splitext(src_img)[1]
                new_img_name = f"kaggle_{set_id}_front_img{ext}"
                dst_img = os.path.join(out_dir, category, new_img_name)

                shutil.copy2(src_img, dst_img)

                labels_data.append(
                    {
                        "subject_id": f"kaggle_{set_id}",
                        "source_image": src_img,
                        "dest_image": dst_img,
                        "height_cm": height_cm,
                        "weight_kg": weight_kg,
                        "bmi": bmi,
                        "body_type": category,
                        "dataset_source": "kaggle",
                    }
                )
                copied_count += 1
    except Exception as e:
        print(f"Kaggle දෝෂයකි: {e}")

    # ==========================================
    # කොටස C: අලුත් Dataset 3 සැකසීම
    # ==========================================
    print("\nDataset 3 දත්ත සකසමින් පවතී...")
    try:
        ds3_df = pd.read_csv(dataset3_csv_path)
        for index, row in ds3_df.iterrows():
            filename = str(row["filename"])
            src_img = os.path.join(dataset3_dir, filename)

            if os.path.exists(src_img):
                try:
                    height_cm = float(row["height_cm"])

                    # බර තීරුව 'weight' හෝ 'weight_kg' ලෙස තිබිය හැක
                    if "weight" in row:
                        weight_kg = float(row["weight"])
                    elif "weight_kg" in row:
                        weight_kg = float(row["weight_kg"])
                    else:
                        continue  # බර නොමැති නම් මඟ හරින්න

                    height_m = height_cm / 100.0
                    bmi = round(weight_kg / (height_m**2), 2)
                    category = (
                        "thin"
                        if bmi < 18.5
                        else "normal" if bmi < 25.0 else "overweight"
                    )

                    set_id = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    new_img_name = f"ds3_{set_id}_front_img{ext}"
                    dst_img = os.path.join(out_dir, category, new_img_name)

                    shutil.copy2(src_img, dst_img)

                    labels_data.append(
                        {
                            "subject_id": f"ds3_{set_id}",
                            "source_image": src_img,
                            "dest_image": dst_img,
                            "height_cm": height_cm,
                            "weight_kg": weight_kg,
                            "bmi": bmi,
                            "body_type": category,
                            "dataset_source": "dataset_3",
                        }
                    )
                    copied_count += 1
                except Exception as e:
                    print(f"දත්ත කියවීමේ දෝෂයකි ({filename}): {e}")
            else:
                print(f"Warning: {filename} පින්තූරය සොයාගත නොහැක.")
    except Exception as e:
        print(f"Dataset 3 දෝෂයකි: {e}")

    # ==========================================
    # අවසාන පියවර: අලුත් Labels CSV සෑදීම
    # ==========================================
    if labels_data:
        labels_df = pd.DataFrame(labels_data)
        labels_df.to_csv(labels_out_path, index=False)
        print(
            f"\nසාර්ථකයි! මුළු පින්තූර {copied_count} ක් වෙන් කර, ඒකාබද්ධ 'labels.csv' නිර්මාණය කරන ලදී."  # noqa: E501
        )
    else:
        print("\nදෝෂයකි: කිසිදු දත්තයක් සකස් කිරීමට නොහැකි විය.")


if __name__ == "__main__":
    prepare_dataset()
