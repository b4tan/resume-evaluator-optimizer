import React from "react";

const DownloadButton = ({ filename }) => {
    const handleDownload = async () => {
        try {
            const response = await fetch(`http://localhost:8000/download_optimized/${filename}`);

            if (!response.ok) {
                throw new Error("Failed to download resume");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Create a temporary <a> tag and trigger the download
            const a = document.createElement("a");
            a.href = url;
            a.download = filename.replace(".pdf", "_optimized.txt"); // Change extension if needed
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // Cleanup
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Download failed:", error);
        }
    };

    return (
        <button 
            onClick={handleDownload} 
            className="px-4 py-2 bg-[#2f53bd] hover:bg-[#4169E1] text-[#EEEBE3] font-medium rounded-lg transition-all duration-200 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
            Download Optimized Resume
        </button>
    );
};

export default DownloadButton;
