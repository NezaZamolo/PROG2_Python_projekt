import os

from export.pdf_exporter import PDFExporter

def generate_weather_pdf(city_data: dict, filename="weather_analysis.pdf"):
    """
    Generate a PDF report for the weather analysis of multiple cities.
    :param city_data:
    :param filename:
    :return:
    """
    pdf = PDFExporter(filename=filename)
    pdf.add_title("Weather Report Summary")

    for city, data in city_data.items():
        # Skip if data is not a dictionary or does not contain "summary"
        if not isinstance(data, dict) or "summary" not in data:
            continue

        pdf.add_new_section(city)

        summary_text = data["summary"]
        summary_dict = {
            line.split(":")[0].strip(): line.split(":")[1].strip()
            for line in summary_text.strip().split("\n") if ":" in line
        }

        anomalies = data.get("anomalies", [])
        if anomalies:
            pdf.add_subheading("Detected Anomalies (Top 5)")
            headers = ["Date", "Temperature Anomaly", "Rainfall Anomaly"]
            pdf.add_table(headers, anomalies)

        extremes = data.get("extremes", [])
        if extremes:
            pdf.add_subheading("Weather Extremes")
            headers = ["Event", "Date", "Value"]
            pdf.add_table(headers, extremes)

        headers = ["Metric", "Value"]
        rows = [[k, v] for k, v in summary_dict.items()]
        pdf.add_table(headers, rows)

        # Add images with captions
        for img in data["images"]:
            img_path = img if img.startswith("plots/") else os.path.join("plots", img)
            caption = f"Figure: {os.path.basename(img).replace('_', ' ').replace('.png', '').title()}"
            pdf.add_image_with_caption(img_path, caption)

    pdf.export()
