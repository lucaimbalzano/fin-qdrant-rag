"use client";
import React, { createContext, useContext, useRef, useState } from "react";
import { cn } from "@/lib/utils";

const MouseEnterContext = createContext<{
  mouseX: number;
  mouseY: number;
}>({
  mouseX: 0,
  mouseY: 0,
});

export const CardContainer = ({
  children,
  className,
  containerClassName,
}: {
  children?: React.ReactNode;
  className?: string;
  containerClassName?: string;
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mouseX, setMouseX] = useState(0);
  const [mouseY, setMouseY] = useState(0);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (rect) {
      setMouseX(event.clientX - rect.left);
      setMouseY(event.clientY - rect.top);
    }
  };

  return (
    <MouseEnterContext.Provider value={{ mouseX, mouseY }}>
      <div
        className={cn("relative", containerClassName)}
        onMouseMove={handleMouseMove}
        ref={containerRef}
      >
        <div className={cn("relative", className)}>{children}</div>
      </div>
    </MouseEnterContext.Provider>
  );
};

export const CardBody = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return <div className={cn("", className)}>{children}</div>;
};

export const CardItem = ({
  as: Tag = "div",
  children,
  className,
  translateX = 0,
  translateY = 0,
  translateZ = 0,
  rotateX = 0,
  rotateY = 0,
  rotateZ = 0,
  ...rest
}: {
  as?: React.ElementType;
  children: React.ReactNode;
  className?: string;
  translateX?: number | string;
  translateY?: number | string;
  translateZ?: number | string;
  rotateX?: number | string;
  rotateY?: number | string;
  rotateZ?: number | string;
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const { mouseX, mouseY } = useContext(MouseEnterContext);

  const rotate3D = (x: number, y: number, z: number) => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const rotateXValue = ((mouseY - centerY) / rect.height) * 2;
      const rotateYValue = ((mouseX - centerX) / rect.width) * 2;

      ref.current.style.transform = `perspective(1000px) rotateX(${
        rotateXValue * x
      }deg) rotateY(${rotateYValue * y}deg) rotateZ(${z}deg) translate3d(${translateX}px, ${translateY}px, ${translateZ}px)`;
    }
  };

  React.useEffect(() => {
    const handleMouseMove = () => {
      rotate3D(rotateX as number, rotateY as number, rotateZ as number);
    };

    const handleMouseLeave = () => {
      if (ref.current) {
        ref.current.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) rotateZ(0deg) translate3d(0px, 0px, 0px)`;
      }
    };

    const element = ref.current;
    if (element) {
      element.addEventListener("mousemove", handleMouseMove);
      element.addEventListener("mouseleave", handleMouseLeave);
      return () => {
        element.removeEventListener("mousemove", handleMouseMove);
        element.removeEventListener("mouseleave", handleMouseLeave);
      };
    }
  }, [mouseX, mouseY, rotateX, rotateY, rotateZ, translateX, translateY, translateZ]);

  const Component = Tag as any;
  return (
    <Component
      ref={ref}
      className={cn("transition-all duration-200 ease-out", className)}
      {...rest}
    >
      {children}
    </Component>
  );
};

// Create a card component that combines all three
export const Card3D = ({
  children,
  className,
  containerClassName,
}: {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
}) => {
  return (
    <CardContainer className={className} containerClassName={containerClassName}>
      <CardBody>{children}</CardBody>
    </CardContainer>
  );
}; 