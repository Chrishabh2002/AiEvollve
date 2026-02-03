export default function ControlToggle({ label, description, checked, onChange }: { label: string, description: string, checked?: boolean, onChange?: (v: boolean) => void }) {
    return (
        <div className="flex items-center justify-between space-x-4">
            <div className="flex flex-col space-y-1">
                <span className="font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">{label}</span>
                <span className="text-sm text-muted-foreground">{description}</span>
            </div>
            {/* Custom Switch Implementation */}
            <button
                type="button"
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 w-11 h-6 ${checked ? 'bg-primary' : 'bg-input'}`}
                role="switch"
                aria-checked={checked}
                onClick={() => onChange && onChange(!checked)}
            >
                <span
                    className={`pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform ${checked ? "translate-x-5" : "translate-x-0"}`}
                />
            </button>
        </div>
    );
}
