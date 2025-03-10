// Modified from ShadCN
import React from "react";

export function Textarea({ className, ...props }) {
    return (
        <textarea
            className={`w-full px-4 py-2 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all duration-200 bg-white dark:bg-gray-800 text-gray-300 ${className}`}
            {...props}
        />
    );
}
