// Modified from ShadCN
import React from "react";

export function Card({ children, className }) {
    return (
        <div className={`bg-white dark:bg-gray-800 shadow-lg rounded-xl p-6 ${className}`}>
            {children}
        </div>
    );
}

export function CardHeader({ children, className }) {
    return <div className={`mb-4 ${className}`}>{children}</div>;
}

export function CardTitle({ children, className }) {
    return <h2 className={`text-xl font-semibold text-gray-900 dark:text-gray-100 ${className}`}>{children}</h2>;
}

export function CardContent({ children, className }) {
    return <div className={`text-gray-700 dark:text-gray-300 ${className}`}>{children}</div>;
}

