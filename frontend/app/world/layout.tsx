import WorldShell from "@/components/WorldShell";

export default function WorldLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <WorldShell>
            {children}
        </WorldShell>
    );
}
