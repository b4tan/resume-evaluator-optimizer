import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Button } from "./Button"; 
import { Textarea } from "./Textarea"; 
import { Card, CardContent, CardHeader, CardTitle } from "./Card"; 

const UploadResume = ({ onUploadComplete }) => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [jobDesc, setJobDesc] = useState("");
    const [loading, setLoading] = useState(false);
    const [responseText, setResponseText] = useState("");

    const handleFileChange = (event) => {
        setSelectedFiles(event.target.files);
    };

    const handleUpload = async () => {
        // Sanity checks
        if (selectedFiles.length === 0) {
            alert("Please upload at least one resume.");
            return;
        }
        if (!jobDesc.trim()) {
            alert("Please enter a job description.");
            return;
        }
        
        const formData = new FormData();
        for (let file of selectedFiles) {
            formData.append("resumes", file);
        }
        formData.append("job_description", jobDesc);
    
        setLoading(true);
        setResponseText("");
    
        try {
            const response = await axios.post("http://127.0.0.1:8000/upload_resumes/", formData);
            setResponseText(response.data.message || "Processing complete.");
            onUploadComplete();
        } catch (error) {
            alert("Error processing the resumes. Please try again.");
            console.error("Error:", error);
        } finally {
            setLoading(false);
        }
    };
    

    return (
        <Card className="w-full max-w-lg border border-gray-600">
            <CardHeader>
                <CardTitle className="text-center font-lighter">Upload Your Resumes</CardTitle>
                <p className="flex flex-col items-center text-gray-400 text-xs font-lighter">
                    Allowed formats are: zip, pdf, and docx
                </p>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex flex-col items-center w-full">
                    <label className="flex items-center justify-center w-1/2 border border-gray-400 text-gray-400 px-4 py-2 rounded-md cursor-pointer text-sm">
                        Choose Files
                        <input type="file" accept=".pdf,.zip,.docx" multiple onChange={handleFileChange} className="hidden" />
                    </label>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                        {selectedFiles.length > 0 ? `${selectedFiles.length} file(s) selected` : "No file chosen"}
                    </p>
                </div>

                <Textarea 
                    placeholder="Enter job description here..." 
                    rows="4" 
                    onChange={(e) => setJobDesc(e.target.value)} 
                />

                <Button onClick={handleUpload} className="w-full" disabled={loading}>
                    {loading ? "Processing..." : "Upload & Analyze"}
                </Button>

                {/* Loading Indicator */}
                {loading && (
                    <div className="flex justify-center mt-4">
                        <div className="h-8 w-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
                    </div>
                )}

                {/* Response Display */}
                {responseText && (
                    <div className="mt-4 p-4 text-center rounded-md bg-gray-100 dark:bg-gray-800 w-full overflow-auto">
                        <ReactMarkdown>{responseText}</ReactMarkdown>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default UploadResume;
