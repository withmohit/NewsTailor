import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Navbar = () => {
  return (
    <header className="border-b border-border bg-background">
      <nav className="container mx-auto flex h-14 items-center justify-between px-4">
        <Link to="/" className="text-xl font-bold tracking-tight text-foreground">
          NEWSTAILOR
        </Link>
        <div className="flex items-center gap-2">
          <Button variant="ghost" asChild>
            <Link to="/signin">Sign In</Link>
          </Button>
          <Button asChild>
            <Link to="/signup">Sign Up</Link>
          </Button>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;
