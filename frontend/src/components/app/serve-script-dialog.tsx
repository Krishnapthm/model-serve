/** Dialog that shows a minimal Python script for calling a served model. */

import { useMemo, useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { IconCheck, IconCopy } from "@tabler/icons-react";
import { toast } from "sonner";
import type { ServedModel } from "@/types/serve";

interface ServeScriptDialogProps {
    model: ServedModel | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

function resolveDynamicBaseUrl(model: ServedModel): string {
    const source = model.endpoint_url;

    try {
        const parsed = new URL(source);
        if (typeof window === "undefined") {
            return parsed.toString();
        }

        return `${parsed.protocol}//${window.location.hostname}${parsed.port ? `:${parsed.port}` : ""}${parsed.pathname}`;
    } catch {
        return source;
    }
}

function buildPythonScript(model: ServedModel, baseUrl: string): string {
    return `# pip install openai
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="${baseUrl}",
)

response = client.chat.completions.create(
    model="${model.model_id}",
    messages=[
        {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
    ],
)

print(response.choices[0].message.content)`;
}

export function ServeScriptDialog({ model, open, onOpenChange }: ServeScriptDialogProps) {
    const [copied, setCopied] = useState(false);

    const script = useMemo(
        () => (model ? buildPythonScript(model, resolveDynamicBaseUrl(model)) : ""),
        [model],
    );

    if (!model) {
        return null;
    }

    const handleCopy = async () => {
        if (!script) return;
        await navigator.clipboard.writeText(script);
        setCopied(true);
        toast.success("Script copied to clipboard");
        setTimeout(() => setCopied(false), 2000);
    };

    const handleOpenChange = (nextOpen: boolean) => {
        if (!nextOpen) {
            setCopied(false);
        }
        onOpenChange(nextOpen);
    };

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogContent className="backdrop-blur-md bg-background/80 border border-border/50 w-[min(96vw,960px)] max-w-[min(96vw,960px)] sm:max-w-[min(96vw,960px)] max-h-[90vh] p-0 gap-0">
                <DialogHeader className="px-5 pt-5 pb-3 border-b border-border/50">
                    <DialogTitle>Python Example Script</DialogTitle>
                    <DialogDescription>
                        {`Use this script with ${model.display_name}. Replace YOUR_API_KEY with a valid key from API Keys.`}
                    </DialogDescription>
                </DialogHeader>

                <ScrollArea className="max-h-[72vh] px-5 pb-5">
                    <div className="pt-4 space-y-3">
                        <Card className="bg-zinc-950 border-zinc-800">
                            <CardContent className="p-4 relative">
                                <pre className="text-sm text-zinc-300 font-mono whitespace-pre-wrap break-words pr-14">
                                    {script}
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
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    );
}
