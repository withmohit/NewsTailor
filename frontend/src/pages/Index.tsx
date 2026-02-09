import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Newspaper, Tag, Clock, ShieldCheck } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const features = [
  { icon: Tag, title: "Choose Your Topics", desc: "Pick categories that matter to you — tech, sports, business, and more." },
  { icon: Clock, title: "Daily Digest", desc: "Get a curated summary delivered to your inbox every morning." },
  { icon: Newspaper, title: "Free Forever", desc: "No hidden fees. Quality news curation at zero cost." },
  { icon: ShieldCheck, title: "Unsubscribe Anytime", desc: "No lock-in. Leave whenever you want, no questions asked." },
];

const Index = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />

      {/* Hero */}
      <section className="container mx-auto flex flex-col items-center px-4 py-24 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          News, Tailored to You
        </h1>
        <p className="mt-4 max-w-md text-lg text-muted-foreground">
          Get curated news delivered to your inbox daily. Choose your topics, stay informed, stay ahead.
        </p>
        <Button size="lg" className="mt-8" asChild>
          <Link to="/signup">Get Started</Link>
        </Button>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 pb-24">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <Card key={f.title} className="border-border shadow-sm">
              <CardContent className="flex flex-col items-center p-6 text-center">
                <f.icon className="mb-3 h-8 w-8 text-primary" />
                <h3 className="font-semibold">{f.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{f.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;
