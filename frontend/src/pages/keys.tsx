/** API Keys page — create, list, revoke API keys. */

import { useState } from "react";
import { useApiKeys, useCreateKey, useRevokeKey } from "@/hooks/useKeys";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { IconPlus, IconTrash, IconCopy, IconCheck, IconKey } from "@tabler/icons-react";
import { toast } from "sonner";

export default function KeysPage() {
    const { data: keys, isLoading } = useApiKeys();
    const createMutation = useCreateKey();
    const revokeMutation = useRevokeKey();

    const [name, setName] = useState("");
    const [createdKey, setCreatedKey] = useState<string | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCreate = async () => {
        if (!name.trim()) return;
        const result = await createMutation.mutateAsync(name.trim());
        setCreatedKey(result.key);
        setName("");
    };

    const handleCopyKey = async () => {
        if (!createdKey) return;
        await navigator.clipboard.writeText(createdKey);
        setCopied(true);
        toast.success("API key copied");
        setTimeout(() => setCopied(false), 2000);
    };

    const handleCloseDialog = () => {
        setDialogOpen(false);
        setCreatedKey(null);
        setName("");
        setCopied(false);
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight">API Keys</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                        Manage API keys for accessing the ModelServe API
                    </p>
                </div>

                <Dialog open={dialogOpen} onOpenChange={(open) => {
                    setDialogOpen(open);
                    if (!open) handleCloseDialog();
                }}>
                    <DialogTrigger asChild>
                        <Button size="sm">
                            <IconPlus size={15} className="mr-1" />
                            Create Key
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="backdrop-blur-md bg-background/80 border border-border/50">
                        {!createdKey ? (
                            <>
                                <DialogHeader>
                                    <DialogTitle>Create API Key</DialogTitle>
                                    <DialogDescription>
                                        Give your key a name to identify it later.
                                    </DialogDescription>
                                </DialogHeader>
                                <Input
                                    placeholder="Key name (e.g. my-project)"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                                />
                                <DialogFooter>
                                    <Button
                                        onClick={handleCreate}
                                        disabled={!name.trim() || createMutation.isPending}
                                    >
                                        {createMutation.isPending ? "Creating..." : "Create"}
                                    </Button>
                                </DialogFooter>
                            </>
                        ) : (
                            <>
                                <DialogHeader>
                                    <DialogTitle>Key Created</DialogTitle>
                                    <DialogDescription>
                                        Copy this key now — it won't be shown again.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="bg-zinc-950 border border-zinc-800 rounded-md p-3 relative">
                                    <code className="text-sm text-zinc-300 font-mono break-all">
                                        {createdKey}
                                    </code>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="absolute top-2 right-2 text-zinc-400 hover:text-zinc-200"
                                        onClick={handleCopyKey}
                                    >
                                        {copied ? <IconCheck size={14} /> : <IconCopy size={14} />}
                                    </Button>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={handleCloseDialog}>
                                        Done
                                    </Button>
                                </DialogFooter>
                            </>
                        )}
                    </DialogContent>
                </Dialog>
            </div>

            {isLoading ? (
                <div className="grid gap-3">
                    {Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-16 w-full rounded-lg" />
                    ))}
                </div>
            ) : (
                <ScrollArea className="h-[calc(100vh-200px)]">
                    <div className="grid gap-3 pr-3">
                        {!keys || keys.length === 0 ? (
                            <Card className="border-dashed">
                                <CardContent className="py-12 text-center">
                                    <IconKey size={40} className="mx-auto text-muted-foreground mb-3" />
                                    <p className="text-sm text-muted-foreground">
                                        No API keys yet. Create one to get started.
                                    </p>
                                </CardContent>
                            </Card>
                        ) : (
                            keys.map((key) => (
                                <Card key={key.id}>
                                    <CardContent className="p-4 flex items-center justify-between">
                                        <div className="space-y-0.5">
                                            <div className="flex items-center gap-2">
                                                <span className="font-medium text-sm">{key.name}</span>
                                                <Badge
                                                    variant="outline"
                                                    className={
                                                        key.is_active
                                                            ? "bg-emerald-500/15 text-emerald-600 border-emerald-500/30"
                                                            : "bg-zinc-500/15 text-zinc-500 border-zinc-500/30"
                                                    }
                                                >
                                                    {key.is_active ? "Active" : "Revoked"}
                                                </Badge>
                                            </div>
                                            <div className="flex gap-3 text-xs text-muted-foreground">
                                                <span className="font-mono">{key.key_prefix}...</span>
                                                <span>Created {new Date(key.created_at).toLocaleDateString()}</span>
                                                {key.last_used_at && (
                                                    <span>Last used {new Date(key.last_used_at).toLocaleDateString()}</span>
                                                )}
                                            </div>
                                        </div>
                                        {key.is_active && (
                                            <AlertDialog>
                                                <AlertDialogTrigger asChild>
                                                    <Button size="sm" variant="ghost" className="text-destructive">
                                                        <IconTrash size={14} />
                                                    </Button>
                                                </AlertDialogTrigger>
                                                <AlertDialogContent className="backdrop-blur-md bg-background/80 border border-border/50">
                                                    <AlertDialogHeader>
                                                        <AlertDialogTitle>Revoke "{key.name}"?</AlertDialogTitle>
                                                        <AlertDialogDescription>
                                                            This key will be permanently deactivated. Any services using it will
                                                            lose access.
                                                        </AlertDialogDescription>
                                                    </AlertDialogHeader>
                                                    <AlertDialogFooter>
                                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                        <AlertDialogAction
                                                            onClick={() => revokeMutation.mutate(key.id)}
                                                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                                        >
                                                            Revoke Key
                                                        </AlertDialogAction>
                                                    </AlertDialogFooter>
                                                </AlertDialogContent>
                                            </AlertDialog>
                                        )}
                                    </CardContent>
                                </Card>
                            ))
                        )}
                    </div>
                </ScrollArea>
            )}
        </div>
    );
}
