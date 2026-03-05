/** Env snippet display with copy-to-clipboard. */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { IconCopy, IconCheck } from "@tabler/icons-react";
import { toast } from "sonner";

interface EnvSnippetProps {
    apiKey: string;
    baseUrl: string;
}

export function EnvSnippet({ apiKey, baseUrl }: EnvSnippetProps) {
    const [copied, setCopied] = useState(false);

    const snippet = `OPENAI_API_KEY=${apiKey}\nOPENAI_BASE_URL=${baseUrl}`;

    const handleCopy = async () => {
        await navigator.clipboard.writeText(snippet);
        setCopied(true);
        toast.success("Copied to clipboard");
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <Card className="bg-zinc-950 border-zinc-800">
            <CardContent className="p-4 relative">
                <pre className="text-sm text-zinc-300 font-mono whitespace-pre-wrap break-all">
                    <span className="text-emerald-400">OPENAI_API_KEY</span>={apiKey}
                    {"\n"}
                    <span className="text-emerald-400">OPENAI_BASE_URL</span>={baseUrl}
                </pre>
                <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-3 right-3 text-zinc-400 hover:text-zinc-200"
                    onClick={handleCopy}
                >
                    {copied ? <IconCheck size={16} /> : <IconCopy size={16} />}
                </Button>
            </CardContent>
        </Card>
    );
}
